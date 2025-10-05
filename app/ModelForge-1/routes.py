import os
import uuid
import json
import zipfile
import json
from datetime import datetime
import tempfile
from datetime import datetime
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from app import app, db
from models import (
    GenerationJob, Project, AssetCache, GeneratedScript, GeneratedEnvironment, 
    ChatMessage, WebhookEndpoint, AssetQueue, AIPack, UserSession
)
from model_generator import generate_3d_model
from file_converter import convert_to_fbx, convert_to_blend
try:
    from instance.ai_modules.chat_handler import ChatHandler
    from instance.ai_modules.script_generator import generate_lua_script
    from instance.ai_modules.environment_generator import generate_environment
except Exception:
    # Provide lightweight stubs so the app can run without optional AI modules
    class ChatHandler:
        def __init__(self, *args, **kwargs):
            pass
        def chat(self, *args, **kwargs):
            return {"response": "AI module not installed. This is a stub response."}
    def generate_lua_script(prompt: str, lang: str):
        return f"-- Stub {lang} script for: {prompt}\n-- (AI module not installed)\n"
    def generate_environment(*args, **kwargs):
        return {"status": "stub", "message": "Environment generator not available"}
from youtube_to_model import YouTubeTo3D
import os
import logging
import io
import tempfile
import trimesh
import subprocess
import shutil
import zipfile

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_session():
    """Get or create user session for tracking preferences and history"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    user_session = UserSession.query.filter_by(session_id=session['session_id']).first()
    if not user_session:
        user_session = UserSession(
            session_id=session['session_id'],
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        db.session.add(user_session)
        db.session.commit()
    
    return user_session

@app.route('/')
def index():
    """Landing page with Studio and download links."""
    return render_template('index.html')

@app.route('/health')
def health():
    import os
    import sys
    logging.info("Health check requested")
    return jsonify({
        'status': 'ok',
        'upload_dir': app.config.get('UPLOAD_FOLDER'),
        'generated_dir': app.config.get('GENERATED_FOLDER'),
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'environment': dict(os.environ),
        'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'not set'),
        'upload_dir_exists': os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads')),
        'generated_dir_exists': os.path.exists(app.config.get('GENERATED_FOLDER', 'generated'))
    })

@app.route('/studio')
def studio():
    """Unified Studio page."""
    return render_template('client_generate.html')

@app.route('/download')
def download_page():
    """Downloads and Installers page."""
    return render_template('download.html')
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        
        if not prompt:
            flash('Please provide a text prompt.', 'error')
            return redirect(url_for('generate'))
        
        # Get user session for preferences
        user_session = get_or_create_session()
        
        # Handle file upload
        reference_image_path = None
        if 'reference_image' in request.files:
            file = request.files['reference_image']
            if file and file.filename and allowed_file(file.filename):
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                reference_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(reference_image_path)
        
        # Get generation options
        material_style = request.form.get('material_style', user_session.material_style_lock)
        generate_variations = request.form.get('generate_variations', 'false').lower() == 'true'
        generate_lod = request.form.get('generate_lod', 'false').lower() == 'true'
        fix_for_roblox = request.form.get('fix_for_roblox', 'true').lower() == 'true'
        
        # Create generation job
        job = GenerationJob(
            prompt=prompt,
            reference_image_path=reference_image_path,
            status='pending',
            material_style=material_style
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Update status to processing
            job.status = 'processing'
            db.session.commit()
            
            # Generate 3D model with advanced parameters
            logging.info(f"Starting 3D model generation for job {job.id}")
            
            # Extract generation parameters from form
            engine = request.form.get('engine', 'hybrid')
            complexity = int(request.form.get('complexity', 7))
            detail_level = int(request.form.get('detail_level', 8))
            material_style = request.form.get('material_style', 'realistic')
            
            # Validate parameters
            complexity = max(1, min(10, complexity))
            detail_level = max(1, min(10, detail_level))
            
            obj_path = generate_3d_model(
                prompt, 
                reference_image_path, 
                job.id,
                engine=engine,
                complexity=complexity,
                detail_level=detail_level,
                material_style=material_style
            )
            
            if not obj_path or not os.path.exists(obj_path):
                raise Exception("Failed to generate 3D model")
            
            # Convert to different formats
            logging.info(f"Converting model to FBX and Blend formats for job {job.id}")
            
            # Try FBX conversion (graceful fallback)
            try:
                fbx_path = convert_to_fbx(obj_path, job.id)
            except Exception as e:
                logging.warning(f"FBX conversion failed: {e}")
                fbx_path = obj_path  # Use OBJ as fallback
            
            # Try Blend conversion (graceful fallback)
            try:
                blend_path = convert_to_blend(obj_path, job.id)
            except Exception as e:
                logging.warning(f"Blend conversion failed: {e}")
                blend_path = None  # Blend conversion is optional
            
            # Generate LOD levels if requested
            lod_levels = {}
            if generate_lod:
                lod_levels = generate_lod_levels(obj_path, job.id)
                job.lod_levels = lod_levels
            
            # Generate variations if requested
            variations = {}
            if generate_variations:
                variations = generate_smart_variations(obj_path, prompt, job.id)
                job.variations = variations
            
            # Fix for Roblox if requested
            if fix_for_roblox:
                roblox_scripts = fix_for_roblox_integration(job.id, prompt)
                job.roblox_scripts = roblox_scripts
                job.roblox_fixed = True
            
            # Generate 3D preview data
            preview_data = generate_3d_preview_data(obj_path, job.id)
            job.preview_data = preview_data
            
            # Update job with results
            job.status = 'completed'
            job.fbx_path = fbx_path
            job.blend_path = blend_path
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            flash('3D model generated successfully!', 'success')
            return redirect(url_for('download', job_id=job.id))
            
        except Exception as e:
            logging.error(f"Error generating 3D model for job {job.id}: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            flash(f'Error generating 3D model: {str(e)}', 'error')
            return redirect(url_for('generate'))
    
    return render_template('generate.html')

# ========== AI HISTORY & FAVORITES ROUTES ==========

@app.route('/history')
def history():
    user_session = get_or_create_session()
    jobs = GenerationJob.query.filter_by(status='completed').order_by(GenerationJob.created_at.desc()).limit(50).all()
    return render_template('history.html', jobs=jobs)

@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
def api_favorites():
    user_session = get_or_create_session()
    
    if request.method == 'GET':
        # Get user's favorite jobs
        favorites = GenerationJob.query.filter_by(is_favorite=True).order_by(GenerationJob.created_at.desc()).all()
        return jsonify([job.to_dict() for job in favorites])
    
    elif request.method == 'POST':
        data = request.get_json()
        job_id = data.get('job_id')
        
        job = GenerationJob.query.get_or_404(job_id)
        job.is_favorite = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Added to favorites'})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        job_id = data.get('job_id')
        
        job = GenerationJob.query.get_or_404(job_id)
        job.is_favorite = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Removed from favorites'})

# ========== ASSET QUEUE & BULK ZIP ROUTES ==========

@app.route('/queue')
def queue():
    user_session = get_or_create_session()
    queues = AssetQueue.query.filter_by(user_id=user_session.session_id).order_by(AssetQueue.created_at.desc()).all()
    return render_template('queue.html', queues=queues)

@app.route('/api/queue', methods=['GET', 'POST'])
def api_queue():
    user_session = get_or_create_session()
    
    if request.method == 'GET':
        queues = AssetQueue.query.filter_by(user_id=user_session.session_id).order_by(AssetQueue.created_at.desc()).all()
        return jsonify([queue.to_dict() for queue in queues])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        queue = AssetQueue(
            name=data['name'],
            user_id=user_session.session_id,
            total_items=len(data.get('prompts', []))
        )
        db.session.add(queue)
        db.session.commit()
        
        # Add generation jobs to queue
        for prompt in data.get('prompts', []):
            job = GenerationJob(
                prompt=prompt,
                status='pending',
                material_style=data.get('material_style')
            )
            db.session.add(job)
            db.session.commit()
            
            queue.assets.append(job)
        
        db.session.commit()
        
        # Start processing queue in background
        from tasks import process_asset_queue_task
        process_asset_queue_task.delay(queue.id)
        
        return jsonify(queue.to_dict())

@app.route('/api/queue/<int:queue_id>/download')
def download_queue_zip(queue_id):
    queue = AssetQueue.query.get_or_404(queue_id)
    
    if queue.status != 'completed' or not queue.zip_path:
        return jsonify({'error': 'Queue not completed or ZIP not available'}), 400
    
    if os.path.exists(queue.zip_path):
        return send_file(
            queue.zip_path,
            as_attachment=True,
            download_name=f'{queue.name}_assets.zip',
            mimetype='application/zip'
        )
    
    return jsonify({'error': 'ZIP file not found'}), 404

# ========== AI PACK BUILDER ROUTES ==========

@app.route('/packs')
def packs():
    packs = AIPack.query.order_by(AIPack.created_at.desc()).all()
    return render_template('packs.html', packs=packs)

@app.route('/api/packs', methods=['GET', 'POST'])
def api_packs():
    if request.method == 'GET':
        packs = AIPack.query.order_by(AIPack.created_at.desc()).all()
        return jsonify([pack.to_dict() for pack in packs])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        pack = AIPack(
            name=data['name'],
            theme=data['theme'],
            description=data.get('description', ''),
            status='generating'
        )
        db.session.add(pack)
        db.session.commit()
        
        # Start pack generation in background
        from tasks import generate_ai_pack_task
        generate_ai_pack_task.delay(pack.id, data['theme'])
        
        return jsonify(pack.to_dict())

@app.route('/api/packs/<int:pack_id>/download')
def download_pack_zip(pack_id):
    pack = AIPack.query.get_or_404(pack_id)
    
    if pack.status != 'completed' or not pack.zip_path:
        return jsonify({'error': 'Pack not completed or ZIP not available'}), 400
    
    if os.path.exists(pack.zip_path):
        return send_file(
            pack.zip_path,
            as_attachment=True,
            download_name=f'{pack.name}_pack.zip',
            mimetype='application/zip'
        )
    
    return jsonify({'error': 'ZIP file not found'}), 404

# ========== SMART VARIATIONS ROUTES ==========

@app.route('/api/variations/<int:job_id>', methods=['POST'])
def generate_variations(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    
    if job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    try:
        variations = generate_smart_variations(job.obj_path, job.prompt, job.id)
        job.variations = variations
        db.session.commit()
        
        return jsonify({'success': True, 'variations': variations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== PACKAGE PROJECT ==========

@app.route('/api/package', methods=['POST'])
def api_package_project():
    """Package the current session's generated OBJ and any reference models into a zip with metadata."""
    try:
        prompt = request.form.get('prompt', '').strip()
        gen_file = request.files.get('generated_obj')
        ref_files = request.files.getlist('ref_models') if 'ref_models' in request.files else []

        if not gen_file:
            return jsonify({'error': 'generated_obj missing'}), 400

        with tempfile.TemporaryDirectory() as tmpdir:
            meta = {
                'prompt': prompt,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'ref_count': len(ref_files),
            }
            meta_path = os.path.join(tmpdir, 'metadata.json')
            with open(meta_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(meta, indent=2))

            assets_dir = os.path.join(tmpdir, 'assets')
            os.makedirs(assets_dir, exist_ok=True)

            gen_path = os.path.join(assets_dir, secure_filename(gen_file.filename) or 'generated.obj')
            gen_file.save(gen_path)

            for rf in ref_files:
                if not rf or not rf.filename:
                    continue
                rf_path = os.path.join(assets_dir, secure_filename(rf.filename))
                rf.save(rf_path)

            zip_path = os.path.join(tmpdir, 'project_package.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(meta_path, arcname='metadata.json')
                for root, _, files in os.walk(assets_dir):
                    for name in files:
                        full = os.path.join(root, name)
                        rel = os.path.relpath(full, tmpdir)
                        zf.write(full, arcname=rel)

            return send_file(zip_path, as_attachment=True, download_name='project_package.zip', mimetype='application/zip')
    except Exception as e:
        logging.error(f"Error in /api/package: {e}")
        return jsonify({'error': str(e)}), 500

def get_blender_path():
    """Attempt to determine Blender executable path.
    Priority: ENV BLENDER_PATH -> common Windows paths -> None
    """
    env_path = os.environ.get('BLENDER_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    # Try common Windows install locations
    possible = [
        r"C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        r"C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe",
    ]
    for p in possible:
        if os.path.exists(p):
            return p
    return None

def run_blender_uv_unwrap(blender_path, input_path, output_path):
    """Run Blender headless to import OBJ/GLB, perform Smart UV Project, and export OBJ.
    """
    script = f"""
import bpy, sys
import os
from math import radians

# Clean scene
bpy.ops.wm.read_homefile(use_empty=True)

in_path = r"{input_path}"
out_path = r"{output_path}"

# Import
ext = os.path.splitext(in_path)[1].lower()
if ext in ['.glb', '.gltf']:
    bpy.ops.import_scene.gltf(filepath=in_path)
else:
    bpy.ops.wm.obj_import(filepath=in_path)

# Select all and unwrap
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.uv.smart_project(island_margin=0.02, angle_limit=radians(66))

# Export OBJ
bpy.ops.wm.obj_export(filepath=out_path, export_selected_objects=False)
"""
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tf:
        tf.write(script)
        temp_script = tf.name
    try:
        cmd = [blender_path, "-b", "-P", temp_script]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        try:
            os.unlink(temp_script)
        except Exception:
            pass

# ========== IMAGE -> 3D (STUB) ==========

@app.route('/api/image_to_3d', methods=['POST'])
def api_image_to_3d():
    """Stub: Accepts an image and optional prompt, returns a placeholder OBJ generated via trimesh.
    This prepares the client flow; later we can replace with TripoSR or a cloud job.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        image_file = request.files['image']
        prompt = request.form.get('prompt', '').lower()

        # Choose a simple primitive based on prompt keywords
        if any(k in prompt for k in ['cube', 'box', 'block']):
            mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
        elif any(k in prompt for k in ['cylinder', 'tube', 'pipe']):
            mesh = trimesh.creation.cylinder(radius=0.5, height=2.0)
        elif any(k in prompt for k in ['chair', 'seat']):
            # Simple chair approximation
            seat = trimesh.creation.box(extents=[1.0, 1.0, 0.1])
            seat.apply_translation([0, 0, 0.8])
            back = trimesh.creation.box(extents=[1.0, 0.1, 1.0])
            back.apply_translation([0, 0.45, 1.3])
            mesh = trimesh.util.concatenate([seat, back])
        else:
            mesh = trimesh.creation.uv_sphere(radius=1.0)

        out_buf = io.BytesIO()
        mesh.export(out_buf, file_type='obj')
        out_buf.seek(0)
        return send_file(out_buf, as_attachment=True, download_name='image3d_placeholder.obj', mimetype='text/plain')
    except Exception as e:
        logging.error(f"Error in /api/image_to_3d: {e}")
        return jsonify({'error': str(e)}), 500

# ========== AUTO-LOD GENERATOR ROUTES ==========

@app.route('/api/lod/<int:job_id>', methods=['POST'])
def generate_lod(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    
    if job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    try:
        lod_levels = generate_lod_levels(job.obj_path, job.id)
        job.lod_levels = lod_levels
        db.session.commit()
        
        return jsonify({'success': True, 'lod_levels': lod_levels})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== FIX FOR ROBLOX ROUTES ==========

@app.route('/api/fix-roblox/<int:job_id>', methods=['POST'])
def fix_for_roblox(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    
    if job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    try:
        roblox_scripts = fix_for_roblox_integration(job.id, job.prompt)
        job.roblox_scripts = roblox_scripts
        job.roblox_fixed = True
        db.session.commit()
        
        return jsonify({'success': True, 'scripts': roblox_scripts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== FREE MODEL AUTO-MATCH ROUTES ==========

@app.route('/api/free-model-match/<int:job_id>', methods=['POST'])
def find_free_model_match(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    
    try:
        free_model_url = find_free_model_match_for_prompt(job.prompt)
        job.free_model_match = free_model_url
        db.session.commit()
        
        return jsonify({'success': True, 'free_model_url': free_model_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 3D PREVIEW ROUTES ==========

@app.route('/api/preview/<int:job_id>')
def get_3d_preview(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    
    if not job.preview_data:
        # Generate preview data if not exists
        if job.obj_path and os.path.exists(job.obj_path):
            preview_data = generate_3d_preview_data(job.obj_path, job.id)
            job.preview_data = preview_data
            db.session.commit()
    
    return jsonify(job.preview_data or {})

# ========== CLIENT-SIDE REFINEMENT API ==========

@app.route('/api/refine', methods=['POST'])
def api_refine():
    """Accepts an uploaded OBJ/GLB from client, performs lightweight fixes, returns refined OBJ."""
    try:
        action = request.form.get('action', 'refine')
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        f = request.files['file']
        if not f.filename:
            return jsonify({'error': 'Empty filename'}), 400

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, f.filename)
            f.save(in_path)

            # Load mesh (trimesh supports obj/glb/gltf)
            mesh = trimesh.load(in_path, force='mesh', process=False)
            if mesh is None or (hasattr(mesh, 'vertices') and len(mesh.vertices) == 0):
                return jsonify({'error': 'Failed to parse mesh'}), 400

            # Basic fixes
            # - remove degenerate faces, fill holes, merge vertices, recompute normals
            try:
                mesh.remove_degenerate_faces()
            except Exception:
                pass
            try:
                mesh.remove_unreferenced_vertices()
            except Exception:
                pass
            try:
                mesh.merge_vertices()
            except Exception:
                pass
            try:
                mesh.rezero()
            except Exception:
                pass
            # Recompute normals
            try:
                mesh.fix_normals()
            except Exception:
                pass

            # UV unwrap via Blender if available
            if action == 'uv_unwrap':
                blender_path = get_blender_path()
                if blender_path and os.path.exists(blender_path):
                    try:
                        uv_out = os.path.join(tmpdir, 'uv_unwrapped.obj')
                        run_blender_uv_unwrap(blender_path, in_path, uv_out)
                        with open(uv_out, 'rb') as fobj:
                            out_data = fobj.read()
                        return send_file(
                            io.BytesIO(out_data),
                            as_attachment=True,
                            download_name='uv_unwrapped.obj',
                            mimetype='text/plain'
                        )
                    except Exception as e:
                        logging.warning(f"Blender UV unwrap failed, falling back: {e}")
                else:
                    logging.info('Blender not available for UV unwrap; returning basic refined mesh')

            # Export refined OBJ
            refined_path = os.path.join(tmpdir, 'refined_model.obj')
            mesh.export(refined_path, file_type='obj')

            if action == 'refine_zip':
                # Create a very simple MTL placeholder and zip package
                mtl_path = os.path.join(tmpdir, 'refined_model.mtl')
                with open(mtl_path, 'w', encoding='utf-8') as fm:
                    fm.write('newmtl default\nKd 0.8 0.8 0.8\n')
                zip_path = os.path.join(tmpdir, 'refined_package.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(refined_path, arcname='refined_model.obj')
                    zf.write(mtl_path, arcname='refined_model.mtl')
                return send_file(
                    zip_path,
                    as_attachment=True,
                    download_name='refined_package.zip',
                    mimetype='application/zip'
                )
            elif action == 'refine_stl':
                # Export refined mesh as STL
                stl_path = os.path.join(tmpdir, 'refined_model.stl')
                mesh.export(stl_path, file_type='stl')
                return send_file(
                    stl_path,
                    as_attachment=True,
                    download_name='refined_model.stl',
                    mimetype='model/stl'
                )
            elif action == 'refine_ply':
                # Export refined mesh as PLY
                ply_path = os.path.join(tmpdir, 'refined_model.ply')
                mesh.export(ply_path, file_type='ply')
                return send_file(
                    ply_path,
                    as_attachment=True,
                    download_name='refined_model.ply',
                    mimetype='model/ply'
                )

            with open(refined_path, 'rb') as fr:
                out_data = fr.read()
            return send_file(
                io.BytesIO(out_data),
                as_attachment=True,
                download_name='refined_model.obj',
                mimetype='text/plain'
            )
    except Exception as e:
        logging.error(f"Error in /api/refine: {e}")
        return jsonify({'error': str(e)}), 500

# ========== USER PREFERENCES ROUTES ==========

@app.route('/api/preferences', methods=['GET', 'PUT'])
def api_preferences():
    user_session = get_or_create_session()
    
    if request.method == 'GET':
        return jsonify(user_session.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        user_session.material_style_lock = data.get('material_style_lock', user_session.material_style_lock)
        user_session.preferred_lod_level = data.get('preferred_lod_level', user_session.preferred_lod_level)
        user_session.auto_generate_variations = data.get('auto_generate_variations', user_session.auto_generate_variations)
        user_session.auto_fix_roblox = data.get('auto_fix_roblox', user_session.auto_fix_roblox)
        user_session.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(user_session.to_dict())

# ========== YOUTUBE TO 3D MODEL ROUTES ==========

@app.route('/youtube-to-3d', methods=['GET', 'POST'])
def youtube_to_3d():
    """Handle YouTube to 3D model generation"""
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        prompt = request.form.get('prompt', 'A 3D model based on the video')
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
            
        try:
            # Initialize YouTube processor
            yt_processor = YouTubeTo3D()
            
            # Download video and extract frames
            video_path = yt_processor.download_video(youtube_url)
            if not video_path:
                return jsonify({'error': 'Failed to download video'}), 500
                
            frames = yt_processor.extract_frames(video_path)
            if not frames:
                return jsonify({'error': 'Failed to extract frames'}), 500
                
            # Generate 3D model
            model_path = yt_processor.generate_3d_model(prompt, frames)
            
            # Create a new generation job
            job = GenerationJob(
                job_id=str(uuid.uuid4()),
                status='completed',
                model_path=str(model_path),
                prompt=prompt,
                source_url=youtube_url
            )
            db.session.add(job)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'job_id': job.job_id,
                'model_path': str(model_path)
            })
            
        except Exception as e:
            app.logger.error(f"Error in YouTube to 3D conversion: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # GET request - show the form
    return render_template('youtube_to_3d.html')

# ========== ADDITIONAL FEATURE ROUTES ==========

# Note: These routes are already defined above, so we don't need to duplicate them here

# ========== HELPER FUNCTIONS ==========

def generate_lod_levels(obj_path, job_id):
    """Generate low, medium, and high LOD versions of the model"""
    try:
        # This would integrate with a 3D processing library like Blender Python API
        # For now, we'll create placeholder file paths
        lod_dir = os.path.join(app.config['GENERATED_FOLDER'], f'job_{job_id}', 'lod')
        os.makedirs(lod_dir, exist_ok=True)
        
        lod_levels = {
            'low': os.path.join(lod_dir, 'low_poly.obj'),
            'medium': os.path.join(lod_dir, 'medium_poly.obj'),
            'high': os.path.join(lod_dir, 'high_poly.obj')
        }
        
        # In a real implementation, you would:
        # 1. Load the original model
        # 2. Apply decimation for low LOD
        # 3. Apply moderate decimation for medium LOD
        # 4. Keep original for high LOD
        # 5. Export each version
        
        return lod_levels
    except Exception as e:
        logging.error(f"Error generating LOD levels: {e}")
        return {}

def generate_smart_variations(obj_path, prompt, job_id):
    """Generate smart variations of the model (different styles, colors, sizes)"""
    try:
        variations_dir = os.path.join(app.config['GENERATED_FOLDER'], f'job_{job_id}', 'variations')
        os.makedirs(variations_dir, exist_ok=True)
        
        # Define variation types
        variation_types = [
            'cartoon_style',
            'realistic_style', 
            'low_poly_style',
            'different_color',
            'different_size'
        ]
        
        variations = {}
        for var_type in variation_types:
            var_path = os.path.join(variations_dir, f'{var_type}.obj')
            # In real implementation, apply AI to generate variations
            variations[var_type] = var_path
        
        return variations
    except Exception as e:
        logging.error(f"Error generating variations: {e}")
        return {}

def fix_for_roblox_integration(job_id, prompt):
    """Generate Lua scripts and fix common Roblox import issues"""
    try:
        scripts_dir = os.path.join(app.config['GENERATED_FOLDER'], f'job_{job_id}', 'roblox_scripts')
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Generate common Roblox scripts
        scripts = {
            'door_script': generate_lua_script(f"Create a door script for {prompt}", 'lua'),
            'animation_script': generate_lua_script(f"Create an animation script for {prompt}", 'lua'),
            'interaction_script': generate_lua_script(f"Create an interaction script for {prompt}", 'lua')
        }
        
        # Save scripts to files
        script_paths = {}
        for script_name, script_content in scripts.items():
            script_path = os.path.join(scripts_dir, f'{script_name}.lua')
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_paths[script_name] = script_path
        
        return script_paths
    except Exception as e:
        logging.error(f"Error fixing for Roblox: {e}")
        return {}

def find_free_model_match_for_prompt(prompt):
    """Find a free model that matches the prompt from external sources"""
    try:
        # This would integrate with APIs like Sketchfab, TurboSquid, etc.
        # For now, return a placeholder URL
        return "https://sketchfab.com/3d-models/example-model"
    except Exception as e:
        logging.error(f"Error finding free model match: {e}")
        return None

def generate_3d_preview_data(obj_path, job_id):
    """Generate 3D preview data for web-based viewer"""
    try:
        # This would generate JSON data for a 3D viewer like Three.js
        # For now, return basic structure
        return {
            'model_url': f'/api/download_file/{job_id}/obj',
            'camera_position': [0, 0, 5],
            'lighting': {
                'ambient': [0.3, 0.3, 0.3],
                'directional': [1, 1, 1]
            }
        }
    except Exception as e:
        logging.error(f"Error generating 3D preview data: {e}")
        return {}

@app.route('/download/<int:job_id>')
def download(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    return render_template('download.html', job=job)

@app.route('/download_file/<int:job_id>/<file_type>')
def download_file(job_id, file_type):
    job = GenerationJob.query.get_or_404(job_id)
    
    if job.status != 'completed':
        flash('Generation not completed yet.', 'error')
        return redirect(url_for('download', job_id=job_id))
    
    if file_type == 'fbx' and job.fbx_path:
        if os.path.exists(job.fbx_path):
            return send_file(job.fbx_path, as_attachment=True, 
                           download_name=f'model_{job_id}.fbx')
    elif file_type == 'blend' and job.blend_path:
        if os.path.exists(job.blend_path):
            return send_file(job.blend_path, as_attachment=True, 
                           download_name=f'model_{job_id}.blend')
    elif file_type == 'obj' and job.obj_path:
        if os.path.exists(job.obj_path):
            return send_file(job.obj_path, as_attachment=True, 
                           download_name=f'model_{job_id}.obj')
    
    flash('File not found.', 'error')
    return redirect(url_for('download', job_id=job_id))

@app.route('/api/job_status/<int:job_id>')
def job_status(job_id):
    job = GenerationJob.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@app.route('/jobs')
def jobs():
    jobs = GenerationJob.query.order_by(GenerationJob.created_at.desc()).limit(20).all()
    return render_template('jobs.html', jobs=jobs)

# ========== PROJECT MANAGEMENT ROUTES ==========

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/api/projects', methods=['GET', 'POST'])
def api_projects():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            project = Project(
                name=data['name'],
                description=data.get('description', ''),
                project_type=data.get('project_type', 'general'),
                status='draft',
                project_data={
                    'generate_assets': data.get('generate_assets', False),
                    'generate_scripts': data.get('generate_scripts', False),
                    'generate_environment': data.get('generate_environment', False)
                }
            )
            
            db.session.add(project)
            db.session.commit()
            
            # TODO: Trigger async project generation if requested
            if data.get('generate_assets') or data.get('generate_scripts') or data.get('generate_environment'):
                # This would trigger the Celery task for project generation
                logging.info(f"Project {project.id} marked for AI generation")
            
            return jsonify(project.to_dict())
            
        except Exception as e:
            logging.error(f"Error creating project: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # GET
        projects = Project.query.order_by(Project.updated_at.desc()).all()
        return jsonify([project.to_dict() for project in projects])

@app.route('/api/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def api_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'GET':
        return jsonify(project.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            project.name = data.get('name', project.name)
            project.description = data.get('description', project.description)
            project.project_type = data.get('project_type', project.project_type)
            project.updated_at = datetime.utcnow()
            
            if 'project_data' in data:
                project.project_data = data['project_data']
            
            db.session.commit()
            return jsonify(project.to_dict())
            
        except Exception as e:
            logging.error(f"Error updating project {project_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # TODO: Clean up associated files and assets
            db.session.delete(project)
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            logging.error(f"Error deleting project {project_id}: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/export')
def export_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    try:
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                # Add project info
                project_info = {
                    'name': project.name,
                    'description': project.description,
                    'type': project.project_type,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                    'data': project.project_data
                }
                zip_file.writestr('project_info.json', json.dumps(project_info, indent=2))
                
                # Add assets
                for asset in project.assets:
                    if asset.obj_path and os.path.exists(asset.obj_path):
                        zip_file.write(asset.obj_path, f'assets/{os.path.basename(asset.obj_path)}')
                    if asset.fbx_path and os.path.exists(asset.fbx_path):
                        zip_file.write(asset.fbx_path, f'assets/{os.path.basename(asset.fbx_path)}')
                    if asset.blend_path and os.path.exists(asset.blend_path):
                        zip_file.write(asset.blend_path, f'assets/{os.path.basename(asset.blend_path)}')
                
                # Add scripts
                for script in project.scripts:
                    if script.file_path and os.path.exists(script.file_path):
                        zip_file.write(script.file_path, f'scripts/{os.path.basename(script.file_path)}')
                    else:
                        # Create script file from content
                        script_filename = f'scripts/{script.name}.{script.script_type}'
                        zip_file.writestr(script_filename, script.content)
                
                # Add environments
                for env in project.environments:
                    if env.file_path and os.path.exists(env.file_path):
                        zip_file.write(env.file_path, f'environments/{os.path.basename(env.file_path)}')
                    else:
                        # Create environment file from data
                        env_filename = f'environments/{env.name}.json'
                        zip_file.writestr(env_filename, json.dumps(env.environment_data, indent=2))
            
            temp_filename = temp_file.name
        
        # Send file and clean up
        def remove_file(response):
            try:
                os.unlink(temp_filename)
            except Exception:
                pass
            return response
        
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name=f'{project.name}_export.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        logging.error(f"Error exporting project {project_id}: {e}")
        flash(f'Error exporting project: {str(e)}', 'error')
        return redirect(url_for('projects'))

# ========== AI CHAT ROUTES ==========

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        project_id = data.get('project_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        # Process message with AI chat handler
        chat_handler = ChatHandler(db.session)
        response_data = chat_handler.process_message(message, session_id, project_id)
        
        # Execute actions if any
        if 'actions' in response_data:
            for action in response_data['actions']:
                try:
                    if action['type'] == 'generate_3d_model':
                        # Create generation job
                        job = GenerationJob(
                            prompt=action['params']['prompt'],
                            status='pending',
                            project_id=action['params'].get('project_id')
                        )
                        db.session.add(job)
                        db.session.commit()
                        
                        response_data['job_id'] = job.id
                        
                    elif action['type'] == 'generate_script':
                        # Generate script
                        script_content = generate_lua_script(
                            action['params']['prompt'],
                            action['params']['script_type']
                        )
                        
                        script = GeneratedScript(
                            name=f"generated_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            script_type=action['params']['script_type'],
                            content=script_content,
                            prompt=action['params']['prompt'],
                            project_id=action['params'].get('project_id')
                        )
                        db.session.add(script)
                        db.session.commit()
                        
                        response_data['script_id'] = script.id
                        
                    elif action['type'] == 'create_project':
                        # Create new project
                        project = Project(
                            name=action['params']['name'],
                            description=action['params']['description'],
                            project_type=action['params'].get('project_type', 'general'),
                            status='draft'
                        )
                        db.session.add(project)
                        db.session.commit()
                        
                        response_data['project_id'] = project.id
                        
                    elif action['type'] == 'generate_environment':
                        # Generate environment
                        env_data = generate_environment(action['params']['prompt'])
                        
                        environment = GeneratedEnvironment(
                            name=f"generated_world_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            environment_type=env_data.get('type', 'unknown'),
                            environment_data=env_data,
                            prompt=action['params']['prompt'],
                            project_id=action['params'].get('project_id')
                        )
                        db.session.add(environment)
                        db.session.commit()
                        
                        response_data['environment_id'] = environment.id
                        
                except Exception as action_error:
                    logging.error(f"Error executing action {action['type']}: {action_error}")
                    # Continue with other actions even if one fails
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in chat API: {e}")
        return jsonify({'error': str(e)}), 500

# ========== SCRIPT GENERATION ROUTES ==========

@app.route('/api/scripts', methods=['GET', 'POST'])
def api_scripts():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Generate script content
            script_content = generate_lua_script(
                data['prompt'],
                data.get('script_type', 'lua')
            )
            
            # Save script
            script = GeneratedScript(
                name=data.get('name', f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                script_type=data.get('script_type', 'lua'),
                content=script_content,
                prompt=data['prompt'],
                project_id=data.get('project_id')
            )
            
            db.session.add(script)
            db.session.commit()
            
            return jsonify(script.to_dict())
            
        except Exception as e:
            logging.error(f"Error generating script: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # GET
        project_id = request.args.get('project_id')
        if project_id:
            scripts = GeneratedScript.query.filter_by(project_id=project_id).all()
        else:
            scripts = GeneratedScript.query.order_by(GeneratedScript.created_at.desc()).limit(50).all()
        
        return jsonify([script.to_dict() for script in scripts])

# ========== ENVIRONMENT GENERATION ROUTES ==========

@app.route('/api/environments', methods=['GET', 'POST'])
def api_environments():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Generate environment
            env_data = generate_environment(data['prompt'])
            
            # Save environment
            environment = GeneratedEnvironment(
                name=data.get('name', f"world_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                environment_type=env_data.get('type', 'unknown'),
                environment_data=env_data,
                prompt=data['prompt'],
                project_id=data.get('project_id')
            )
            
            db.session.add(environment)
            db.session.commit()
            
            return jsonify(environment.to_dict())
            
        except Exception as e:
            logging.error(f"Error generating environment: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # GET
        project_id = request.args.get('project_id')
        if project_id:
            environments = GeneratedEnvironment.query.filter_by(project_id=project_id).all()
        else:
            environments = GeneratedEnvironment.query.order_by(GeneratedEnvironment.created_at.desc()).limit(50).all()
        
        return jsonify([env.to_dict() for env in environments])

# ========== N8N WEBHOOK INTEGRATION ROUTES ==========

@app.route('/api/webhooks', methods=['GET', 'POST'])
def api_webhooks():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            webhook = WebhookEndpoint(
                name=data['name'],
                endpoint_url=data['endpoint_url'],
                secret_key=data.get('secret_key', ''),
                event_types=data.get('event_types', []),
                config=data.get('config', {})
            )
            
            db.session.add(webhook)
            db.session.commit()
            
            return jsonify(webhook.to_dict())
            
        except Exception as e:
            logging.error(f"Error creating webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # GET
        webhooks = WebhookEndpoint.query.filter_by(is_active=True).all()
        return jsonify([webhook.to_dict() for webhook in webhooks])

@app.route('/api/webhooks/<int:webhook_id>', methods=['GET', 'PUT', 'DELETE'])
def api_webhook(webhook_id):
    webhook = WebhookEndpoint.query.get_or_404(webhook_id)
    
    if request.method == 'GET':
        return jsonify(webhook.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            webhook.name = data.get('name', webhook.name)
            webhook.endpoint_url = data.get('endpoint_url', webhook.endpoint_url)
            webhook.secret_key = data.get('secret_key', webhook.secret_key)
            webhook.is_active = data.get('is_active', webhook.is_active)
            webhook.event_types = data.get('event_types', webhook.event_types)
            webhook.config = data.get('config', webhook.config)
            
            db.session.commit()
            return jsonify(webhook.to_dict())
            
        except Exception as e:
            logging.error(f"Error updating webhook {webhook_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(webhook)
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            logging.error(f"Error deleting webhook {webhook_id}: {e}")
            return jsonify({'error': str(e)}), 500

# n8n webhook endpoint (public endpoint for n8n to trigger)
@app.route('/webhook/n8n/<webhook_name>', methods=['POST'])
def n8n_webhook(webhook_name):
    """
    Public webhook endpoint for n8n integration
    Usage: POST /webhook/n8n/your_webhook_name
    """
    try:
        # Find webhook by name
        webhook = WebhookEndpoint.query.filter_by(name=webhook_name, is_active=True).first()
        if not webhook:
            return jsonify({'error': 'Webhook not found or inactive'}), 404
        
        data = request.get_json()
        
        # Verify secret key if provided
        if webhook.secret_key:
            provided_secret = request.headers.get('X-Webhook-Secret') or data.get('secret')
            if provided_secret != webhook.secret_key:
                return jsonify({'error': 'Invalid secret key'}), 401
        
        # Process webhook based on action
        action = data.get('action', 'unknown')
        
        if action == 'generate_model':
            # Create 3D model generation job
            job = GenerationJob(
                prompt=data.get('prompt', ''),
                status='pending',
                project_id=data.get('project_id')
            )
            db.session.add(job)
            db.session.commit()
            
            # TODO: Trigger async generation
            
            response_data = {
                'success': True,
                'job_id': job.id,
                'message': 'Model generation job created'
            }
            
        elif action == 'generate_script':
            # Generate script
            script_content = generate_lua_script(
                data.get('prompt', ''),
                data.get('script_type', 'lua')
            )
            
            script = GeneratedScript(
                name=data.get('name', f"webhook_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                script_type=data.get('script_type', 'lua'),
                content=script_content,
                prompt=data.get('prompt', ''),
                project_id=data.get('project_id')
            )
            db.session.add(script)
            db.session.commit()
            
            response_data = {
                'success': True,
                'script_id': script.id,
                'content': script_content,
                'message': 'Script generated successfully'
            }
            
        elif action == 'create_project':
            # Create new project
            project = Project(
                name=data.get('name', f"n8n_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                description=data.get('description', ''),
                project_type=data.get('project_type', 'general'),
                status='draft'
            )
            db.session.add(project)
            db.session.commit()
            
            response_data = {
                'success': True,
                'project_id': project.id,
                'message': 'Project created successfully'
            }
            
        elif action == 'get_status':
            # Return system status
            total_projects = Project.query.count()
            total_assets = GenerationJob.query.filter_by(status='completed').count()
            
            response_data = {
                'success': True,
                'status': 'online',
                'total_projects': total_projects,
                'total_assets': total_assets,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        else:
            response_data = {
                'success': False,
                'error': f'Unknown action: {action}',
                'available_actions': ['generate_model', 'generate_script', 'create_project', 'get_status']
            }
        
        # Update webhook statistics
        webhook.trigger_count = (webhook.trigger_count or 0) + 1
        webhook.last_triggered = datetime.utcnow()
        db.session.commit()
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error processing n8n webhook {webhook_name}: {e}")
        return jsonify({'error': str(e)}), 500

# ========== CACHE MANAGEMENT ROUTES ==========

@app.route('/api/cache', methods=['GET', 'DELETE'])
def api_cache():
    if request.method == 'GET':
        cache_entries = AssetCache.query.order_by(AssetCache.last_accessed.desc()).limit(100).all()
        return jsonify([entry.to_dict() for entry in cache_entries])
    
    elif request.method == 'DELETE':
        try:
            # Clear all cache entries
            cache_entries = AssetCache.query.all()
            for entry in cache_entries:
                if entry.file_path and os.path.exists(entry.file_path):
                    try:
                        os.unlink(entry.file_path)
                    except Exception:
                        pass
                db.session.delete(entry)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Cache cleared successfully'})
            
        except Exception as e:
            logging.error(f"Error clearing cache: {e}")
            return jsonify({'error': str(e)}), 500

# ========== ASSET CONVERSION ROUTES ==========

@app.route('/api/convert', methods=['POST'])
def convert_asset():
    """Convert FBX/BLEND/OBJ files to Roblox-friendly formats"""
    try:
        data = request.get_json()
        input_path = data.get('input_path')
        output_formats = data.get('formats', ['fbx', 'obj'])
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input file not found'}), 400
        
        # Generate unique job ID for this conversion
        job_id = str(uuid.uuid4())
        
        # Create output directory
        output_dir = os.path.join("generated", f"conversion_{job_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        
        # Convert to requested formats
        if 'fbx' in output_formats:
            try:
                fbx_path = convert_to_fbx(input_path, job_id)
                if fbx_path and os.path.exists(fbx_path):
                    results['fbx'] = fbx_path
            except Exception as e:
                logging.warning(f"FBX conversion failed: {e}")
        
        if 'blend' in output_formats:
            try:
                blend_path = convert_to_blend(input_path, job_id)
                if blend_path and os.path.exists(blend_path):
                    results['blend'] = blend_path
            except Exception as e:
                logging.warning(f"Blend conversion failed: {e}")
        
        if 'obj' in output_formats and not input_path.endswith('.obj'):
            try:
                # Convert to OBJ using Blender
                obj_path = convert_with_blender_to_obj(input_path, job_id)
                if obj_path and os.path.exists(obj_path):
                    results['obj'] = obj_path
            except Exception as e:
                logging.warning(f"OBJ conversion failed: {e}")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'results': results,
            'download_urls': {
                format: f'/api/download_converted/{job_id}/{format}'
                for format in results.keys()
            }
        })
        
    except Exception as e:
        logging.error(f"Error in asset conversion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_converted/<job_id>/<file_format>')
def download_converted(job_id, file_format):
    """Download converted asset files"""
    try:
        file_path = os.path.join("generated", f"model_{job_id}.{file_format}")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'converted_{job_id}.{file_format}'
        )
        
    except Exception as e:
        logging.error(f"Error downloading converted file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_map', methods=['POST'])
def build_nova_map():
    """Build N.O.V.A.-style lobby/map from existing assets"""
    try:
        data = request.get_json()
        map_name = data.get('name', 'nova_lobby')
        asset_paths = data.get('assets', [])
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create map generation job
        job = GenerationJob(
            prompt=f"N.O.V.A. space station lobby/map: {map_name}",
            status='processing',
            project_id=data.get('project_id')
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Process and combine assets into a complete map
            map_result = build_space_station_map(asset_paths, job.id, map_name)
            
            job.status = 'completed'
            job.fbx_path = map_result.get('fbx_path')
            job.obj_path = map_result.get('obj_path')
            job.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'job_id': job.id,
                'map_data': map_result,
                'download_url': f'/download/{job.id}'
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            raise
        
    except Exception as e:
        logging.error(f"Error building N.O.V.A. map: {e}")
        return jsonify({'error': str(e)}), 500

def convert_with_blender_to_obj(input_path, job_id):
    """Convert any 3D file to OBJ using Blender"""
    try:
        blender_cmd = find_blender_executable()
        if not blender_cmd:
            raise Exception("Blender not found")
        
        output_path = os.path.join("generated", f"model_{job_id}.obj")
        
        script_content = f'''
import bpy
import os

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import file based on extension
input_path = "{input_path}"
if input_path.endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=input_path)
elif input_path.endswith('.blend'):
    bpy.ops.wm.open_mainfile(filepath=input_path)
elif input_path.endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=input_path)

# Export as OBJ
bpy.ops.export_scene.obj(filepath="{output_path}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        try:
            cmd = [blender_cmd, '--background', '--python', script_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"Blender conversion failed: {result.stderr}")
            
            return output_path if os.path.exists(output_path) else None
            
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
                
    except Exception as e:
        logging.error(f"Error converting to OBJ: {e}")
        return None

def build_space_station_map(asset_paths, job_id, map_name):
    """Build a complete N.O.V.A.-style space station map"""
    try:
        import trimesh
        import numpy as np
        
        # Load and process existing assets
        assets = []
        
        # Process scifi-panel
        panel_path = r"c:\Users\dell\Downloads\ModelForge-original\scifi-panel (1)\source\SM_Panel_3_embedded.fbx"
        if os.path.exists(panel_path):
            try:
                # Convert to OBJ first for easier processing
                panel_obj = convert_with_blender_to_obj(panel_path, f"{job_id}_panel")
                if panel_obj:
                    panel_mesh = trimesh.load(panel_obj)
                    assets.append(('panel', panel_mesh))
            except Exception as e:
                logging.warning(f"Failed to load panel: {e}")
        
        # Process spaceship corridor
        corridor_path = r"c:\Users\dell\Downloads\ModelForge-original\spaceship_corridor_obj\Spaceship Corridor_obj\Spaceship corridor.obj"
        if os.path.exists(corridor_path):
            try:
                corridor_mesh = trimesh.load(corridor_path)
                assets.append(('corridor', corridor_mesh))
            except Exception as e:
                logging.warning(f"Failed to load corridor: {e}")
        
        # Process reactor
        reactor_path = r"c:\Users\dell\Downloads\ModelForge-original\reactor.fbx"
        if os.path.exists(reactor_path):
            try:
                reactor_obj = convert_with_blender_to_obj(reactor_path, f"{job_id}_reactor")
                if reactor_obj:
                    reactor_mesh = trimesh.load(reactor_obj)
                    assets.append(('reactor', reactor_mesh))
            except Exception as e:
                logging.warning(f"Failed to load reactor: {e}")
        
        # Build the map layout
        map_components = []
        
        # Central corridor as main structure
        for name, mesh in assets:
            if name == 'corridor':
                # Place corridor at center
                mesh.apply_translation([0, 0, 0])
                map_components.append(mesh)
                
                # Add panels along the corridor walls
                for i, (panel_name, panel_mesh) in enumerate([(n, m) for n, m in assets if n == 'panel']):
                    # Left wall panels
                    left_panel = panel_mesh.copy()
                    left_panel.apply_translation([-5, 0, i * 3])
                    left_panel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                    map_components.append(left_panel)
                    
                    # Right wall panels
                    right_panel = panel_mesh.copy()
                    right_panel.apply_translation([5, 0, i * 3])
                    right_panel.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [0, 0, 1]))
                    map_components.append(right_panel)
        
        # Add reactor rooms
        for i, (name, mesh) in enumerate([(n, m) for n, m in assets if n == 'reactor']):
            # Place reactors in side rooms
            reactor_copy = mesh.copy()
            side = 1 if i % 2 == 0 else -1
            reactor_copy.apply_translation([side * 8, 0, i * 6])
            map_components.append(reactor_copy)
        
        # Combine all components
        if map_components:
            combined_map = trimesh.util.concatenate(map_components)
            
            # Save as OBJ and FBX
            obj_path = os.path.join("generated", f"{map_name}_{job_id}.obj")
            combined_map.export(obj_path)
            
            # Convert to FBX
            fbx_path = convert_to_fbx(obj_path, f"{map_name}_{job_id}")
            
            return {
                'obj_path': obj_path,
                'fbx_path': fbx_path,
                'components_used': len(map_components),
                'map_name': map_name
            }
        else:
            raise Exception("No assets could be loaded")
            
    except Exception as e:
        logging.error(f"Error building space station map: {e}")
        raise

# Note: These routes and functions are already defined above, so we don't need to duplicate them here
