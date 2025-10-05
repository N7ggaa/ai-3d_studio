#!/usr/bin/env python3
"""
ModelForge Local Bridge Service
- Lists generated variants from logs/variants.jsonl
- Serves per-variant manifest JSON from generated/variants/auto/*.manifest.json
- Serves thumbnails from logs/thumbs/*.png

Install:
  pip install -r requirements.txt

Run (from the ModelForge-1 directory):
  python -m uvicorn bridge_service:app --host 127.0.0.1 --port 8765 --reload

Roblox Studio plugin should call localhost only.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any
import os
import requests
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

def _detect_base_dir() -> Path:
    """Detect the project base directory that contains 'logs/' and 'generated/variants/auto/'.
    Order of precedence:
    1) MODELFORGE_BASE environment variable if valid
    2) Current file's directory and its parents (up to 3 levels)
    Fallback: current file's directory
    """
    env_base = os.environ.get('MODELFORGE_BASE')
    if env_base:
        p = Path(env_base).expanduser().resolve()
        if (p / 'logs').exists() and (p / 'generated' / 'variants' / 'auto').exists():
            return p

    here = Path(__file__).resolve().parent

    def is_valid(base: Path) -> bool:
        return (base / 'logs').exists() and (base / 'generated' / 'variants' / 'auto').exists()

    candidates = [here, here.parent, here.parent.parent, here.parent.parent.parent]
    for c in candidates:
        try:
            if is_valid(c):
                return c
        except Exception:
            continue

    return here

BASE_DIR = _detect_base_dir()
LOGS_DIR = BASE_DIR / 'logs'
OUT_DIR = BASE_DIR / 'generated' / 'variants' / 'auto'
THUMBS_DIR = LOGS_DIR / 'thumbs'
DEV_MAX_RESULTS = 0
try:
    DEV_MAX_RESULTS = int(os.environ.get('DEV_MAX_RESULTS', '0') or '0')
except Exception:
    DEV_MAX_RESULTS = 0

app = FastAPI(title="ModelForge Bridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_variants_log() -> List[Dict[str, Any]]:
    jsonl = LOGS_DIR / 'variants.jsonl'
    items: List[Dict[str, Any]] = []
    if not jsonl.exists():
        return items
    try:
        with open(jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and 'name' in obj:
                        items.append(obj)
                except Exception:
                    continue
    except Exception:
        pass
    return items


def _latest_unique_by_name(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Keep last occurrence per name (jsonl grows over time)
    by_name: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        by_name[r['name']] = r
    return list(by_name.values())


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/variants')
def list_variants(limit: int = 200, order: str = 'score', offset: int = 0, q: str | None = None, batch: str | None = None):
    """List variants with basic metadata and URLs."""
    rows = _latest_unique_by_name(_load_variants_log())
    # Optional filters
    if q:
        ql = q.lower()
        rows = [r for r in rows if ql in str(r.get('name', '')).lower()]
    if batch is not None:
        rows = [r for r in rows if str(r.get('batch')) == str(batch)]
    # derive score and sort (lower is better)
    def s(row):
        try:
            return float(row.get('score_total', 1e9))
        except Exception:
            return 1e9
    if order == 'score':
        rows.sort(key=s)
    elif order == 'recent':
        # jsonl read order already last write wins; no timestamp in rows, so keep as-is
        pass
    # Dev cap to keep responses small when developing
    if DEV_MAX_RESULTS > 0 and len(rows) > DEV_MAX_RESULTS:
        rows = rows[:DEV_MAX_RESULTS]
    # Build payload
    out = []
    if offset < 0:
        offset = 0
    window = rows[offset:offset + max(0, int(limit))]
    for r in window:
        name = r.get('name', '')
        out.append({
            'name': name,
            'batch': r.get('batch'),
            'variant': r.get('variant'),
            'score_total': r.get('score_total'),
            'chunks': r.get('chunks'),
            'faces_total': r.get('faces_total'),
            'manifest_url': f"/variant/{name}",
            'thumb_url': f"/thumb/{name}.png",
        })
    return out


@app.get('/variant/{name}')
def get_variant_manifest(name: str):
    """Return manifest JSON for a given variant name."""
    manifest_path = OUT_DIR / f"{name}.manifest.json"
    if not manifest_path.exists():
        # Attempt to generate name from prefix if chunk-suffixed was passed
        if name.endswith('.manifest.json'):
            manifest_path = OUT_DIR / name
        else:
            # Allow raw file passthrough if exact filename given
            alt = OUT_DIR / name
            if alt.exists():
                manifest_path = alt
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="Manifest not found")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read manifest")


@app.get('/thumb/{filename}')
def get_thumbnail(filename: str):
    """Serve thumbnail image for a variant."""
    p = THUMBS_DIR / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(str(p))


@app.get('/file/auto/{filename}')
def get_file_auto(filename: str):
    """Serve a raw file from generated/variants/auto (OBJ/FBX/manifest). Useful for local inspection."""
    p = OUT_DIR / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    # Let Starlette infer media type
    return FileResponse(str(p))


@app.get('/best')
def get_best(limit: int = 50, offset: int = 0, q: str | None = None, batch: str | None = None):
    rows = _latest_unique_by_name(_load_variants_log())
    # Optional filters
    if q:
        ql = q.lower()
        rows = [r for r in rows if ql in str(r.get('name', '')).lower()]
    if batch is not None:
        rows = [r for r in rows if str(r.get('batch')) == str(batch)]
    try:
        rows.sort(key=lambda r: float(r.get('score_total', 1e9)))
    except Exception:
        pass
    # Dev cap
    if DEV_MAX_RESULTS > 0 and len(rows) > DEV_MAX_RESULTS:
        rows = rows[:DEV_MAX_RESULTS]
    out = []
    if offset < 0:
        offset = 0
    window = rows[offset:offset + max(0, int(limit))]
    for r in window:
        name = r.get('name', '')
        out.append({
            'name': name,
            'score_total': r.get('score_total'),
            'manifest_url': f"/variant/{name}",
            'thumb_url': f"/thumb/{name}.png",
            'batch': r.get('batch'),
            'variant': r.get('variant'),
            'chunks': r.get('chunks'),
        })
    return out


@app.post('/generate')
def trigger_generate():
    # Placeholder: orchestrating the generator loop is out of scope here
    # This endpoint exists for future: could enqueue a task or signal a running process
    raise HTTPException(status_code=501, detail="Not implemented in local-first bridge")


@app.post('/upload/{name}')
def upload_to_open_cloud(
    name: str,
    asset_type: str = "Model",
    dry_run: bool = False,
    poll: bool = True,
    poll_timeout: int = 120,
    poll_interval: float = 1.5,
):
    """Upload the selected variant's FBX to Roblox Open Cloud Assets API.

    Query params:
    - asset_type: Roblox asset type name (e.g., "Model"). Default: Model
    - dry_run: if true, do not upload; just return resolved paths and metadata

    Requires env vars:
    - ROBLOX_API_KEY: Open Cloud API key with Assets permissions
    - ROBLOX_GROUP_ID or ROBLOX_USER_ID: creator context
    """
    # Resolve manifest
    manifest_path = OUT_DIR / f"{name}.manifest.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="Manifest not found for variant")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read manifest")

    # Choose primary FBX from first chunk
    try:
        chunks = manifest.get('chunks') or []
        if not chunks:
            raise ValueError('No chunks in manifest')
        fbx_rel = chunks[0]['fbx_path']
        fbx_abs = (BASE_DIR / fbx_rel).resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Manifest missing fbx_path")
    if not fbx_abs.exists():
        raise HTTPException(status_code=404, detail="FBX file not found on disk")

    # Dry run support for debugging in Studio without making external calls
    if dry_run:
        return {
            'name': name,
            'asset_type': asset_type,
            'fbx_path': str(fbx_abs),
            'creator': {
                'group_id': os.environ.get('ROBLOX_GROUP_ID'),
                'user_id': os.environ.get('ROBLOX_USER_ID')
            },
            'note': 'Dry run only. No upload performed.'
        }

    # Environment configuration (only required for real uploads)
    api_key = os.environ.get('ROBLOX_API_KEY')
    group_id = os.environ.get('ROBLOX_GROUP_ID')
    user_id = os.environ.get('ROBLOX_USER_ID')
    if not api_key:
        raise HTTPException(status_code=400, detail="ROBLOX_API_KEY not set in environment")
    if not group_id and not user_id:
        raise HTTPException(status_code=400, detail="Set either ROBLOX_GROUP_ID or ROBLOX_USER_ID in environment")

    # Compose request to Roblox Open Cloud Assets API
    url = 'https://apis.roblox.com/assets/v1/assets'
    headers = {
        'x-api-key': api_key,
    }
    # The exact payload fields depend on Roblox Open Cloud configuration; we use a common pattern
    # If your org requires different fields, adjust as needed.
    request_payload: Dict[str, Any] = {
        'displayName': name,
        'description': 'Uploaded by ModelForge Bridge',
        'assetType': asset_type,
        'creationContext': ({'groupId': int(group_id)} if group_id else {'userId': int(user_id)}),
    }
    files = {
        'fileContent': (fbx_abs.name, open(fbx_abs, 'rb'), 'application/octet-stream'),
    }
    data = {
        'request': json.dumps(request_payload),
    }
    try:
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=120)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach Roblox Open Cloud: {e}")
    finally:
        try:
            files['fileContent'][1].close()
        except Exception:
            pass

    if not (200 <= resp.status_code < 300):
        # Bubble up error text for debugging
        raise HTTPException(status_code=resp.status_code, detail=f"Roblox API error: {resp.text}")

    try:
        payload = resp.json()
    except Exception:
        payload = {'raw': resp.text}

    # Derive a convenient asset_id if present in the payload
    asset_id = None
    if isinstance(payload, dict):
        asset_id = payload.get('assetId') or payload.get('id')

    # If Roblox returned an operation, optionally poll until done
    op_id = None
    op_path = None
    if isinstance(payload, dict):
        op_id = payload.get('operationId')
        op_path = payload.get('path')
    if poll and (op_id or (isinstance(op_path, str) and '/operations/' in op_path)):
        if not op_id and op_path:
            try:
                op_id = op_path.rsplit('/', 1)[-1]
            except Exception:
                op_id = None
        if op_id:
            ops_url = f'https://apis.roblox.com/assets/v1/operations/{op_id}'
            deadline = time.time() + max(1, int(poll_timeout))
            last_status: Dict[str, Any] | None = None
            while time.time() < deadline:
                try:
                    op_resp = requests.get(ops_url, headers=headers, timeout=30)
                    if not (200 <= op_resp.status_code < 300):
                        last_status = {'status': op_resp.status_code, 'text': op_resp.text}
                    else:
                        op_json = op_resp.json()
                        if isinstance(op_json, dict) and op_json.get('done'):
                            resp_payload = op_json.get('response') or {}
                            asset_id2 = None
                            if isinstance(resp_payload, dict):
                                asset_id2 = resp_payload.get('assetId') or resp_payload.get('id')
                            return JSONResponse(content={
                                'name': name,
                                'asset_type': asset_type,
                                'fbx_file': fbx_abs.name,
                                'asset_id': asset_id2,
                                'roblox_response': op_json,
                                'polled': True,
                            })
                except Exception:
                    pass
                time.sleep(max(0.1, float(poll_interval)))
            # Timed out
            return JSONResponse(content={
                'name': name,
                'asset_type': asset_type,
                'fbx_file': fbx_abs.name,
                'asset_id': asset_id,
                'roblox_response': payload,
                'note': 'Polling timed out',
                'polled': True,
                'last_status': last_status,
            }, status_code=202)

    # Expect payload to include the created asset's ID; exact field names may vary
    return JSONResponse(content={
        'name': name,
        'asset_type': asset_type,
        'fbx_file': fbx_abs.name,
        'asset_id': asset_id,
        'roblox_response': payload,
    })
