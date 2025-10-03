## Repository Inventory and Classification

### Keep (Core)
- `ModelForge/` – Web client/server (React + Express + Drizzle)
- `ModelForge/shared/` – Types/schema for DB
- `ModelForge-1/` – Python generation worker (headless endpoints); Electron shell base

### Archive (Non-core, still valuable)
- `VideoTo3D/` – Roblox Lua plugin (standalone)
- `ModelForge-optimized/VideoTo3D/` – Optimized variant of Roblox plugin
- `prompt2roblox/plugin/` – Roblox plugin generator outputs
- `ModelForge-1/src/**/*.lua` – Roblox plugin code within `ModelForge-1`
- `ModelForge-1/tests/**/*.lua` – Lua tests
- `prompt2roblox/` – FastAPI backend for YouTube→Roblox; not in core desktop flow

### Evaluate (Experimental/Legacy)
- `ModelForge-1/*` scripts like `demo_*`, `nova_*`, `training/`, `youtube_to_model.py` – keep if used by worker pipeline; otherwise archive to `archive/experiments/`

### Build Artifacts / Large Binaries (ignore or attach to release)
- `ModelForge/dist/`, `ModelForge/uploads/`, `ModelForge-1/generated/`, `ModelForge-1/uploads/`, `*.fbx`, `*.blend`, `attached_assets/`

### Next Actions
- Use `scripts/archive_non_core.ps1` to perform moves into `archive/` with an index README.
- Re-run web and worker builds to confirm green.


