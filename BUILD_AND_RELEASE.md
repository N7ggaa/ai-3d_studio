## Build, Package, and Release

### Prereqs
- Node 20+, PNPM or NPM
- Python 3.11+
- (Optional) Blender installed for FBX/BLEND

### Web (Marketing + API)
- Install: `cd ModelForge && npm ci`
- Dev: `npm run dev` (Vite + Express)
- Build: `npm run build && npm run preview`

### Python Worker (Headless)
- Create venv and install: `python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
- Run worker API: `python app.py` or `python main.py` (headless endpoints only)

### Desktop (Electron)
- Install deps in `ModelForge-1/electron`
- Start in dev linking to local web client: `npm run dev`
- Package: `npm run build` -> artifacts in `dist/`

### Release Flow
1. Tag repo `vX.Y.Z`.
2. CI builds: web bundle, worker wheel, electron installers for Win/macOS.
3. Attach artifacts to GitHub Release and update website download links.

### Verification
- Smoke tests: run `npm test` (web), `pytest` (worker).
- Manual QA checklist for desktop app startup, generation, export.


