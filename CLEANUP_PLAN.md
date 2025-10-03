## Debloat and Consolidation Plan

### Goals
- Reduce footprint by archiving non-core modules (especially Roblox/Lua).
- Keep a single, high-quality path: Desktop app + local Python worker + optional web API.
- Preserve reproducibility and document everything.

### Classification
- Keep:
  - `ModelForge/client`, `ModelForge/server`, `ModelForge/shared`
  - `ModelForge-1` (Python worker) – but use headless endpoints only
  - `ModelForge-1/electron` as base for desktop shell
- Archive:
  - `VideoTo3D/`, `ModelForge-optimized/VideoTo3D/`, `prompt2roblox/plugin/`
  - Lua code in `ModelForge-1/src/**`, `ModelForge-1/tests/**` (Lua)
  - Legacy demos and experimental scripts not in the production flow
- Remove (after archive grace period): build artifacts, temporary generated data, redundant docs

### Steps
1) Create `archive/` and move Roblox/Lua/plugin projects into `archive/roblox_plugins/`.
2) Move experimental scripts to `archive/experiments/` with a README index.
3) Add `.editorconfig` and tighten `.gitignore` for generated/logs.
4) Ensure `ModelForge` web build runs after archive moves.
5) Ensure Python worker runs headless; disable Flask UI routes not needed by desktop.
6) Wire Electron to React client and local worker, add environment schema.
7) CI: lint/build/test for `ModelForge` and smoke tests for Python worker.

### Archive Policy
- Minimum 60 days in `archive/` before deletion.
- Add `ARCHIVED_README.md` in each archived subdir with purpose and last known run instructions.

### Risk Controls
- No deletions before CI green.
- Git tag `pre-archive` before moves.
- Document manual rollback steps.

