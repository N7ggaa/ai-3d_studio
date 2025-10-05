import os
import logging
import zipfile
import json
from datetime import datetime
from celery import current_task
from app import db
from models import GenerationJob, Project, AssetCache
from model_generator import generate_3d_model
from file_converter import convert_to_fbx, convert_to_blend
from instance.ai_modules.script_generator import generate_lua_script
from instance.ai_modules.environment_generator import generate_environment

def generate_3d_model_task(job_id, prompt, reference_image_path=None, project_id=None):
    """
    Async task for 3D model generation with progress tracking
    """
    try:
        # Update job status
        job = GenerationJob.query.get(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        job.status = 'processing'
        job.task_id = current_task.request.id
        db.session.commit()
        
        # Update progress: Starting generation
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Initializing AI models...'}
        )
        
        # Check cache first
        cache_key = f"model_{hash(prompt)}"
        cached_result = AssetCache.query.filter_by(cache_key=cache_key).first()
        
        if cached_result and os.path.exists(cached_result.file_path):
            logging.info(f"Using cached result for prompt: {prompt}")
            job.obj_path = cached_result.file_path
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 50, 'total': 100, 'status': 'Using cached model...'}
            )
        else:
            # Generate new model
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 20, 'total': 100, 'status': 'Generating 3D model...'}
            )
            
            obj_path = generate_3d_model(prompt, reference_image_path, job_id)
            job.obj_path = obj_path
            
            # Cache the result
            cache_entry = AssetCache(
                cache_key=cache_key,
                file_path=obj_path,
                asset_type='model',
                meta_data={'prompt': prompt}
            )
            db.session.add(cache_entry)
        
        # Convert to different formats
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 60, 'total': 100, 'status': 'Converting to FBX format...'}
        )
        
        fbx_path = convert_to_fbx(job.obj_path, job_id)
        job.fbx_path = fbx_path
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Converting to Blender format...'}
        )
        
        blend_path = convert_to_blend(job.obj_path, job_id)
        job.blend_path = blend_path
        
        # Complete job
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        
        # Add to project if specified
        if project_id:
            project = Project.query.get(project_id)
            if project:
                project.assets.append(job)
        
        db.session.commit()
        
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Generation completed!'}
        )
        
        return {
            'job_id': job_id,
            'status': 'completed',
            'fbx_path': fbx_path,
            'blend_path': blend_path
        }
        
    except Exception as e:
        logging.error(f"Error in generate_3d_model_task: {str(e)}")
        
        # Update job with error
        job = GenerationJob.query.get(job_id)
        if job:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
        
        current_task.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Error: {str(e)}'}
        )
        
        raise

def generate_game_project_task(project_id, description):
    """
    Async task for complete game project generation
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            raise Exception(f"Project {project_id} not found")
        
        project.status = 'processing'
        project.task_id = current_task.request.id
        db.session.commit()
        
        # Parse description into tasks
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Analyzing project description...'}
        )
        
        # This would use AI to break down the description
        tasks = parse_project_description(description)
        
        total_tasks = len(tasks)
        completed_tasks = 0
        
        for i, task in enumerate(tasks):
            progress = 20 + (60 * i // total_tasks)
            current_task.update_state(
                state='PROGRESS',
                meta={'current': progress, 'total': 100, 'status': f'Processing: {task["type"]}...'}
            )
            
            if task['type'] == 'model':
                # Generate 3D model
                job = GenerationJob(
                    prompt=task['prompt'],
                    status='pending',
                    project_id=project_id
                )
                db.session.add(job)
                db.session.commit()
                
                generate_3d_model_task(job.id, task['prompt'], project_id=project_id)
                
            elif task['type'] == 'script':
                # Generate Lua script
                script_content = generate_lua_script(task['prompt'])
                script_path = save_script(script_content, project_id, task['name'])
                
            elif task['type'] == 'environment':
                # Generate environment layout
                env_data = generate_environment(task['prompt'])
                save_environment(env_data, project_id)
        
        # Complete project
        project.status = 'completed'
        project.completed_at = datetime.utcnow()
        db.session.commit()
        
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Project generation completed!'}
        )
        
        return {'project_id': project_id, 'status': 'completed'}
        
    except Exception as e:
        logging.error(f"Error in generate_game_project_task: {str(e)}")
        
        project = Project.query.get(project_id)
        if project:
            project.status = 'failed'
            project.error_message = str(e)
            db.session.commit()
        
        current_task.update_state(
            state='FAILURE',
            meta={'status': f'Error: {str(e)}'}
        )
        
        raise

def parse_project_description(description):
    """
    Parse natural language description into specific tasks
    This would use an LLM in production
    """
    # Simplified task extraction for demo
    tasks = []
    
    description_lower = description.lower()
    
    # Detect models needed
    if 'spaceship' in description_lower:
        tasks.append({'type': 'model', 'prompt': 'futuristic spaceship', 'name': 'spaceship'})
    if 'car' in description_lower:
        tasks.append({'type': 'model', 'prompt': 'realistic car', 'name': 'car'})
    if 'building' in description_lower:
        tasks.append({'type': 'model', 'prompt': 'modern building', 'name': 'building'})
    
    # Detect scripts needed
    if 'npc' in description_lower:
        tasks.append({'type': 'script', 'prompt': 'NPC interaction system', 'name': 'npc_controller'})
    if 'quest' in description_lower:
        tasks.append({'type': 'script', 'prompt': 'quest management system', 'name': 'quest_manager'})
    
    # Detect environment
    if 'world' in description_lower or 'map' in description_lower:
        tasks.append({'type': 'environment', 'prompt': description, 'name': 'main_world'})
    
    return tasks

def save_script(content, project_id, name):
    """Save generated script to project"""
    script_dir = os.path.join("generated", f"project_{project_id}", "scripts")
    os.makedirs(script_dir, exist_ok=True)
    
    script_path = os.path.join(script_dir, f"{name}.lua")
    with open(script_path, 'w') as f:
        f.write(content)
    
    return script_path

def save_environment(env_data, project_id):
    """Save environment data to project"""
    env_dir = os.path.join("generated", f"project_{project_id}", "environments")
    os.makedirs(env_dir, exist_ok=True)
    
    import json
    env_path = os.path.join(env_dir, "main_world.json")
    with open(env_path, 'w') as f:
        json.dump(env_data, f, indent=2)
    
    return env_path

def process_asset_queue_task(queue_id):
    """Process asset queue and generate bulk ZIP"""
    try:
        from models import AssetQueue, GenerationJob
        
        queue = AssetQueue.query.get(queue_id)
        if not queue:
            raise Exception(f"Queue {queue_id} not found")
        
        queue.status = 'processing'
        db.session.commit()
        
        # Process each asset in the queue
        for i, asset in enumerate(queue.assets):
            try:
                # Generate 3D model
                obj_path = generate_3d_model(asset.prompt, asset.reference_image_path, asset.id)
                
                if obj_path and os.path.exists(obj_path):
                    # Convert to different formats
                    fbx_path = convert_to_fbx(obj_path, asset.id)
                    blend_path = convert_to_blend(obj_path, asset.id)
                    
                    # Update asset
                    asset.status = 'completed'
                    asset.obj_path = obj_path
                    asset.fbx_path = fbx_path
                    asset.blend_path = blend_path
                    asset.completed_at = datetime.utcnow()
                    
                    queue.completed_items += 1
                    db.session.commit()
                
            except Exception as e:
                logging.error(f"Error processing asset {asset.id}: {e}")
                asset.status = 'failed'
                asset.error_message = str(e)
                db.session.commit()
        
        # Create bulk ZIP file
        if queue.completed_items > 0:
            zip_path = create_bulk_zip(queue)
            queue.zip_path = zip_path
        
        queue.status = 'completed'
        queue.completed_at = datetime.utcnow()
        db.session.commit()
        
        return {'queue_id': queue_id, 'status': 'completed'}
        
    except Exception as e:
        logging.error(f"Error processing asset queue {queue_id}: {e}")
        
        queue = AssetQueue.query.get(queue_id)
        if queue:
            queue.status = 'failed'
            db.session.commit()
        
        raise

def generate_ai_pack_task(pack_id, theme):
    """Generate themed AI pack with multiple assets"""
    try:
        from models import AIPack, GenerationJob
        
        pack = AIPack.query.get(pack_id)
        if not pack:
            raise Exception(f"Pack {pack_id} not found")
        
        pack.status = 'generating'
        db.session.commit()
        
        # Define assets based on theme
        theme_assets = get_theme_assets(theme)
        
        generated_assets = []
        for asset_prompt in theme_assets:
            try:
                # Create generation job
                job = GenerationJob(
                    prompt=asset_prompt,
                    status='pending',
                    pack_id=pack_id
                )
                db.session.add(job)
                db.session.commit()
                
                # Generate 3D model
                obj_path = generate_3d_model(asset_prompt, None, job.id)
                
                if obj_path and os.path.exists(obj_path):
                    # Convert to different formats
                    fbx_path = convert_to_fbx(obj_path, job.id)
                    blend_path = convert_to_blend(obj_path, job.id)
                    
                    # Update job
                    job.status = 'completed'
                    job.obj_path = obj_path
                    job.fbx_path = fbx_path
                    job.blend_path = blend_path
                    job.completed_at = datetime.utcnow()
                    
                    generated_assets.append(job)
                    pack.asset_count += 1
                    db.session.commit()
                
            except Exception as e:
                logging.error(f"Error generating asset for pack: {e}")
        
        # Create themed pack ZIP
        if generated_assets:
            zip_path = create_themed_pack_zip(pack, generated_assets)
            pack.zip_path = zip_path
        
        pack.status = 'completed'
        pack.completed_at = datetime.utcnow()
        db.session.commit()
        
        return {'pack_id': pack_id, 'status': 'completed'}
        
    except Exception as e:
        logging.error(f"Error generating AI pack {pack_id}: {e}")
        
        pack = AIPack.query.get(pack_id)
        if pack:
            pack.status = 'failed'
            db.session.commit()
        
        raise

def get_theme_assets(theme):
    """Get list of assets to generate for a specific theme"""
    theme_assets = {
        'medieval': [
            'medieval castle tower',
            'medieval house',
            'medieval wall',
            'medieval gate',
            'medieval furniture',
            'medieval weapons'
        ],
        'sci-fi': [
            'futuristic spaceship',
            'sci-fi laboratory',
            'alien creature',
            'futuristic weapon',
            'space station',
            'robot'
        ],
        'fantasy': [
            'magical tree',
            'dragon',
            'wizard tower',
            'magical portal',
            'fantasy creature',
            'enchanted weapon'
        ],
        'modern': [
            'modern house',
            'office building',
            'modern car',
            'furniture',
            'electronics',
            'modern weapon'
        ]
    }
    
    return theme_assets.get(theme, ['generic asset'])

def create_bulk_zip(queue):
    """Create bulk ZIP file for asset queue"""
    try:
        zip_dir = os.path.join("generated", "queues")
        os.makedirs(zip_dir, exist_ok=True)
        
        zip_path = os.path.join(zip_dir, f"queue_{queue.id}_{queue.name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for asset in queue.assets:
                if asset.status == 'completed':
                    # Add model files
                    if asset.obj_path and os.path.exists(asset.obj_path):
                        zip_file.write(asset.obj_path, f"{asset.id}/model.obj")
                    if asset.fbx_path and os.path.exists(asset.fbx_path):
                        zip_file.write(asset.fbx_path, f"{asset.id}/model.fbx")
                    if asset.blend_path and os.path.exists(asset.blend_path):
                        zip_file.write(asset.blend_path, f"{asset.id}/model.blend")
        
        return zip_path
        
    except Exception as e:
        logging.error(f"Error creating bulk ZIP: {e}")
        return None

def create_themed_pack_zip(pack, assets):
    """Create themed pack ZIP file"""
    try:
        zip_dir = os.path.join("generated", "packs")
        os.makedirs(zip_dir, exist_ok=True)
        
        zip_path = os.path.join(zip_dir, f"pack_{pack.id}_{pack.name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add pack info
            pack_info = {
                'name': pack.name,
                'theme': pack.theme,
                'description': pack.description,
                'asset_count': len(assets),
                'created_at': pack.created_at.isoformat() if pack.created_at else None
            }
            zip_file.writestr('pack_info.json', json.dumps(pack_info, indent=2))
            
            # Add assets
            for asset in assets:
                if asset.status == 'completed':
                    asset_dir = f"assets/{asset.id}"
                    
                    if asset.obj_path and os.path.exists(asset.obj_path):
                        zip_file.write(asset.obj_path, f"{asset_dir}/model.obj")
                    if asset.fbx_path and os.path.exists(asset.fbx_path):
                        zip_file.write(asset.fbx_path, f"{asset_dir}/model.fbx")
                    if asset.blend_path and os.path.exists(asset.blend_path):
                        zip_file.write(asset.blend_path, f"{asset_dir}/model.blend")
        
        return zip_path
        
    except Exception as e:
        logging.error(f"Error creating themed pack ZIP: {e}")
        return None