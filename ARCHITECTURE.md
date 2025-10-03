## AI3D Studio – Target Architecture

### Vision
High‑quality prompt‑to‑3D application with a clean, maintainable codebase. Website provides downloads and docs; desktop app performs local generation with optional cloud APIs.

### Core Components (kept)
- **Web (Website + Dashboard)**: `ModelForge/client` (React + Vite + Tailwind + shadcn/ui).
- **Web API**: `ModelForge/server` (Express + TypeScript + Drizzle ORM for Postgres). Serves marketing pages, auth, download links, job metadata.
- **Generation Engine (Local Worker)**: `ModelForge-1` (Python + Flask services) used headlessly as a local worker process for 3D generation, conversion (OBJ/FBX/BLEND), and utilities. Flask UI not used in desktop mode.
- **Electron Desktop Shell**: `ModelForge-1/electron` adapted to wrap the React client and communicate with the local Python worker.

### Components to Archive (candidate)
- Roblox Studio plugins and Lua code: `VideoTo3D/`, `ModelForge-optimized/VideoTo3D/`, `prompt2roblox/plugin/`, `ModelForge-1/src/**/*.lua`, tests in Lua. These will move to `archive/roblox_plugins/` to de-bloat core.
- Experimental scripts and legacy demos under `ModelForge-1/` that aren't in the production path (see CLEANUP_PLAN.md).

### High-Level Data Flow
1. User initiates a generation request from desktop app UI.
2. Electron invokes local Python worker HTTP API (Flask) or CLI.
3. Worker generates geometry (procedural/AI), exports OBJ/FBX/BLEND to `generated/`.
4. Metadata persisted by local SQLite; optionally synced to Postgres via web API when online.
5. UI shows progress via polling/websocket to local worker; finished assets are shown with preview and a Save/Export button.

### Technology Choices
- Frontend: React + TypeScript, Vite, Tailwind, shadcn/ui, TanStack Query, Wouter.
- Desktop: Electron (Node 20+), secure IPC; Python worker spawned as child process on app start.
- Backend (web): Express + TypeScript, Drizzle, Postgres.
- Worker (local): Python 3.11+, Flask micro-API (headless), Trimesh, Blender (optional) for FBX/BLEND.

### Interfaces
- Desktop↔Worker: HTTP loopback (127.0.0.1:PORT) with token; file I/O via dedicated `generated/` dir.
- Desktop↔Web API: Authenticated REST for release checks, crash reports, and optional cloud queues.

### Security/Privacy
- Local generation by default; no uploads without user opt‑in.
- API keys stored in OS keychain/secure storage; never in plain text files.
- Strict input validation on worker endpoints and extension whitelists.

### Observability
- Structured logs (JSON) in app data dir; rotating files.
- Crash reports are opt‑in with redaction.

### Roadmap Notes
- Replace Flask UI with headless worker endpoints only.
- Consolidate config into a single `.env` per environment with schema validation.

