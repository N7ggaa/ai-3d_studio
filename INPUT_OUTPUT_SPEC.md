## Input / Output Specification

### Inputs
- Prompt: string (1–500 chars)
- Optional reference image(s): PNG/JPG ≤ 10 MB each
- Generation settings: quality preset, polygon budget, texture size, seed, format targets (OBJ/FBX/BLEND)

### Worker API (Local)
- POST `/generate`
  - body: `{ prompt, images?, settings }`
  - returns: `{ jobId }`
- GET `/jobs/{id}`
  - returns: `{ status: pending|running|failed|completed, progress?, message?, outputs? }`
- GET `/jobs/{id}/assets`
  - returns: file list with paths, sizes, hashes

### Outputs
- Geometry: OBJ always; FBX/BLEND if Blender installed
- Textures: PNG in `generated/{jobId}/textures/`
- Metadata JSON: `generated/{jobId}/metadata.json` with provenance and settings
- Preview images: PNG thumbnails

### File Structure
```
generated/
  {jobId}/
    model.obj
    model.fbx (optional)
    model.blend (optional)
    textures/
    previews/
    metadata.json
```

### Validation
- Strict extension whitelist; image type sniffing; max file and total size
- Sanitized filenames; isolate per‑job directories

### Performance Targets
- Cold start < 10s (without Blender); generation typical 20–120s depending on quality
- Memory ceiling default 6–8 GB; configurable

### Telemetry (opt‑in)
- Success/failure counts, durations, anonymized settings, no prompts unless user opts in

