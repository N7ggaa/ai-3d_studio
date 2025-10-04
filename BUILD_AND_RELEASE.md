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

### Deployment

#### Static Website (industries-web)
- **GitHub Pages**: Automatically deployed via `.github/workflows/deploy-pages.yml` on push to main
- **Netlify**: Automatically deployed via `.github/workflows/deploy-netlify.yml` on push to main
  - Requires `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` secrets in GitHub repository

#### Flask Web App (app/ModelForge-1)
- **Docker**: Build and push image via `.github/workflows/docker.yml`
- **Container Platforms**: Deploy the Docker image to:
  - Railway
  - Render
  - Heroku
  - DigitalOcean App Platform
  - AWS/GCP/Azure container services
- **Note**: Cannot be deployed to GitHub Pages or Netlify due to dynamic nature (requires server-side Python execution)

#### Desktop App (Electron)
- Package for distribution: `npm run build` in `ModelForge-1/electron`
- Artifacts generated in `dist/` directory

### Verification
- Smoke tests: run `npm test` (web), `pytest` (worker).
- Manual QA checklist for desktop app startup, generation, export.
- Health check endpoint: `/health` for Flask app status


