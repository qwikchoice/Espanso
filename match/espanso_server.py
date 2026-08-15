#!/usr/bin/env python3
"""
Espanso Manager — local API server
No external packages required (stdlib only).

Usage:  python espanso_server.py
        Then open http://localhost:7890/ in any browser.
"""

import errno
import json
import os
import shutil
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# ── CONFIG ────────────────────────────────────────────────────
MATCH_DIR   = Path(__file__).parent.resolve()
BASE_FILE   = MATCH_DIR / "base.yml"
META_FILE   = MATCH_DIR / "base.meta.json"
ARCHIVE_DIR = MATCH_DIR / "archive"
HTML_FILE   = MATCH_DIR / "espanso-manager.html"
HOST        = "127.0.0.1"
PORT        = int(os.environ.get("ESPANSO_MANAGER_PORT", 7890))
MAX_BACKUPS = 5
# ──────────────────────────────────────────────────────────────


def backup_count():
    return len(sorted(MATCH_DIR.glob("base_backup_*.yml")))


def latest_backup_label():
    backups = sorted(MATCH_DIR.glob("base_backup_*.yml"))
    if not backups:
        return None
    return backups[-1].stem.replace("base_backup_", "").replace("_", " ")


def do_backup_and_save(yaml_content: str, meta_dict: dict):
    """Create timestamped backup, archive old ones, then write main files."""
    ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"base_backup_{ts}.yml"

    # Write new backup
    (MATCH_DIR / name).write_text(yaml_content, encoding="utf-8")

    # Collect & sort all backups
    backups = sorted(MATCH_DIR.glob("base_backup_*.yml"))

    # Archive excess
    if len(backups) > MAX_BACKUPS:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        for old in backups[:-MAX_BACKUPS]:
            shutil.move(str(old), str(ARCHIVE_DIR / old.name))

    # Write main files
    BASE_FILE.write_text(yaml_content, encoding="utf-8")
    META_FILE.write_text(
        json.dumps(meta_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── HTTP HANDLER ──────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence default access log

    # ── helpers ───────────────────────────────────────────────
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type",   "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, text):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type",   "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def send_err(self, msg, status=500):
        self.send_json({"error": msg}, status)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    # ── OPTIONS (CORS preflight) ───────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── GET ────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path

        # ── Serve the app UI
        if path in ("/", "/index.html", "/espanso-manager.html"):
            if not HTML_FILE.exists():
                self.send_err("espanso-manager.html not found in match folder", 404)
                return
            self.send_html(HTML_FILE.read_text(encoding="utf-8"))

        # ── Load base.yml + metadata + backup info
        elif path == "/api/load":
            yaml_text = BASE_FILE.read_text(encoding="utf-8") if BASE_FILE.exists() else ""
            try:
                meta = json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {}
            except Exception:
                meta = {}
            self.send_json({
                "yaml":         yaml_text,
                "meta":         meta,
                "folder":       str(MATCH_DIR),
                "backupCount":  backup_count(),
                "latestBackup": latest_backup_label(),
            })

        # ── Backup list
        elif path == "/api/backups":
            backups  = [b.name for b in sorted(MATCH_DIR.glob("base_backup_*.yml"))]
            archived = [a.name for a in sorted(ARCHIVE_DIR.glob("base_backup_*.yml"))] \
                       if ARCHIVE_DIR.exists() else []
            self.send_json({"backups": backups, "archived": archived})

        else:
            self.send_err("Not found", 404)

    # ── POST ───────────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_body()
            data = json.loads(body) if body else {}

            # ── Save (triggered on every CRUD change)
            if path == "/api/save":
                yaml_content = data.get("yaml", "")
                meta_dict    = data.get("meta", {})
                do_backup_and_save(yaml_content, meta_dict)
                self.send_json({
                    "ok":           True,
                    "backupCount":  backup_count(),
                    "latestBackup": latest_backup_label(),
                })

            else:
                self.send_err("Unknown endpoint", 404)

        except json.JSONDecodeError as e:
            self.send_err(f"JSON parse error: {e}")
        except Exception as e:
            self.send_err(str(e))


# ── MAIN ──────────────────────────────────────────────────────
def create_server(host: str, port: int, max_tries: int = 10):
    for attempt in range(max_tries):
        candidate_port = port + attempt
        try:
            return HTTPServer((host, candidate_port), Handler), candidate_port
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
    raise OSError(f"Could not bind to {host}:{port} after {max_tries} attempts")


def main():
    try:
        server, bound_port = create_server(HOST, PORT)
    except OSError as exc:
        print("Failed to start Espanso Manager:", exc)
        return

    url = f"http://localhost:{bound_port}/"
    print("=" * 52)
    print("  ⚡ Espanso Manager")
    print(f"  Folder : {MATCH_DIR}")
    print(f"  URL    : {url}")
    if bound_port != PORT:
        print(f"  Note   : port {PORT} was in use, using {bound_port} instead.")
    print("  Press Ctrl+C to stop.")
    print("=" * 52)

    # Open browser after a short delay
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
