# Espanso Manager

Visual CRUD interface for Espanso text expansions — backups, archiving, export/import, search, tags, and notes.

---

## Requirements

- Python 3 (stdlib only, no pip installs needed)
- Chrome or Edge (for File System Access API)

---

## Installation

### Windows

1. Copy this `match` folder into your Espanso config directory:
   ```
   %AppData%\espanso\match
   ```
2. Run `windows\start_espanso.bat` — double-click it.
3. Browser opens automatically at `http://localhost:7890`.

> **Python not found?** Download from https://python.org — check "Add Python to PATH" during install.

---

### Mac

1. Copy this `match` folder into your Espanso config directory:
   ```
   ~/Library/Application Support/espanso/match
   ```
2. Run the launcher:
   - **Double-click:** `mac/start_espanso.command` (opens Terminal automatically)
   - **Terminal:** `./mac/start_espanso.sh`

   First run may show a macOS security prompt — click **Open**.

3. Browser opens automatically at `http://localhost:7890`.

> **Python not found?** Run `brew install python` or download from https://python.org.

---

## File Structure

```
match/
├── base.yml                  ← your Espanso snippets (edit via the UI)
├── base.meta.json            ← tags/notes metadata
├── espanso_server.py         ← local API server
├── espanso-manager.html      ← UI (served by the server)
├── windows/
│   └── start_espanso.bat     ← Windows launcher
├── mac/
│   ├── start_espanso.command ← Mac launcher (double-click)
│   └── start_espanso.sh      ← Mac launcher (terminal)
└── archive/                  ← auto-archived old backups
```

---

## Usage

- **Server mode** (recommended): use a launcher above — no folder picker needed.
- **Standalone mode**: open `espanso-manager.html` directly in Chrome/Edge, then click "Open Espanso Folder" and grant access to the `match` folder.

Backups are created automatically on every save. Up to 5 backups stay in `match/`; older ones move to `archive/`.
