## Desktop Packaging (Electron)

### Overview
Electron wraps the React UI and communicates with the local Python worker. The renderer serves the built React app; the main process spawns the worker and manages its lifecycle.

### App Structure
- Main process: starts Flask worker on a random localhost port; exposes secure IPC to renderer.
- Renderer: React app (built with Vite) loads from `file://` or `app://` and talks to worker over `https://127.0.0.1:{port}` with a token.

### Steps
1. Build web client: `cd ModelForge && npm run build` (outputs to `ModelForge/dist/public`).
2. Copy/serve web bundle inside Electron app.
3. On app ready, spawn Python worker:
   - Use bundled Python or system Python (detect).
   - Create venv on first run; install `requirements.txt` if missing.
   - Start `app.py` with env var `WORKER_TOKEN` and `WORKER_PORT=0` (auto-port).
4. Health check worker before showing UI.

### Security
- Random token per session; pass to renderer via secure IPC only.
- Disable NodeIntegration in renderer; use contextIsolation.
- Code signing for release builds.

### Packaging Targets
- Windows: NSIS installer + portable zip
- macOS: dmg + universal binary if feasible
- Linux: AppImage

### Build Commands (example)
- Dev: `npm run dev` (Electron + Vite dev server)
- Package: `npm run build` → installers in `dist/`

### Auto-Update
- Optional: Use GitHub Releases provider; check on startup and offer download.

### Crash Handling
- Capture main/renderer crashes, write logs to user data dir, offer opt‑in report upload.

