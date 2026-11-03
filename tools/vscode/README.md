# VS Code files

Copy `tasks.json`, `launch.json` and `settings.json` into the repository's `.vscode/` folder (create it if needed). Then:

- **Terminal → Run Task → Dashboard** (or Ctrl+Shift+B, the default build task) starts the dashboard from the project `.venv`; it opens at http://localhost:8501. Close the terminal panel to stop it.
- **Run → Dashboard (Streamlit)** (F5) starts it under the debugger, with breakpoints in `app/` and `src/`.
- **Terminal → Run Task → Tests** runs pytest; the test explorer is configured too.

The paths assume Windows (`.venv\Scripts\python.exe`); the task file also carries the Linux and macOS commands.
