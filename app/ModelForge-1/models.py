from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy instance
db = SQLAlchemy()

# Association table for project assets
project_assets = db.Table('project_assets',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('generation_job_id', db.Integer, db.ForeignKey('generation_job.id'), primary_key=True)
)

# Association table for favorites
user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.String(255), primary_key=True),  # Session ID or user ID
    db.Column('generation_job_id', db.Integer, db.ForeignKey('generation_job.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# Association table for asset queue
asset_queue_items = db.Table('asset_queue_items',
    db.Column('queue_id', db.Integer, db.ForeignKey('asset_queue.id'), primary_key=True),
    db.Column('generation_job_id', db.Integer, db.ForeignKey('generation_job.id'), primary_key=True)
)

class GenerationJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    reference_image_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    obj_path = db.Column(db.String(255))
    fbx_path = db.Column(db.String(255))
    blend_path = db.Column(db.String(255))
    error_message = db.Column(db.Text)
    task_id = db.Column(db.String(255))  # Celery task ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    # New fields for enhanced features
    is_favorite = db.Column(db.Boolean, default=False)
    material_style = db.Column(db.String(50))  # cartoon, realistic, low-poly, etc.
    lod_levels = db.Column(JSON)  # Store LOD file paths
    variations = db.Column(JSON)  # Store variation file paths
    roblox_fixed = db.Column(db.Boolean, default=False)
    roblox_scripts = db.Column(JSON)  # Store generated Lua scripts
    preview_data = db.Column(JSON)  # Store 3D preview data
    free_model_match = db.Column(db.String(500))  # URL to free model if AI couldn't make it
    pack_id = db.Column(db.Integer, db.ForeignKey('ai_pack.id'))  # If part of a themed pack
    
    # Relationships
    favorites_users = db.relationship('GenerationJob', secondary=user_favorites, backref='favorited_by')
    queue_items = db.relationship('AssetQueue', secondary=asset_queue_items, backref='queued_assets')
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'status': self.status,
            'obj_path': self.obj_path,
            'fbx_path': self.fbx_path,
            'blend_path': self.blend_path,
            'error_message': self.error_message,
            'task_id': self.task_id,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_favorite': self.is_favorite,
            'material_style': self.material_style,
            'lod_levels': self.lod_levels,
            'variations': self.variations,
            'roblox_fixed': self.roblox_fixed,
            'roblox_scripts': self.roblox_scripts,
            'preview_data': self.preview_data,
            'free_model_match': self.free_model_match,
            'pack_id': self.pack_id
        }

class AssetQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)  # Session ID or user ID
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    total_items = db.Column(db.Integer, default=0)
    completed_items = db.Column(db.Integer, default=0)
    zip_path = db.Column(db.String(500))  # Path to bulk ZIP file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    assets = db.relationship('GenerationJob', secondary=asset_queue_items, backref='queues')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'status': self.status,
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'zip_path': self.zip_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        }

class AIPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(100), nullable=False)  # medieval, sci-fi, etc.
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='generating')  # generating, completed, failed
    zip_path = db.Column(db.String(500))  # Path to themed pack ZIP
    asset_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    assets = db.relationship('GenerationJob', backref='pack')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'theme': self.theme,
            'description': self.description,
            'status': self.status,
            'zip_path': self.zip_path,
            'asset_count': self.asset_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50), default='general')  # roblox, unity, general
    status = db.Column(db.String(50), default='draft')  # draft, processing, completed, failed
    task_id = db.Column(db.String(255))  # Celery task ID for project generation
    error_message = db.Column(db.Text)
    
    # Project data
    project_data = db.Column(JSON)  # Store project configuration and metadata
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    assets = db.relationship('GenerationJob', secondary=project_assets, backref='projects')
    scripts = db.relationship('GeneratedScript', backref='project', lazy='dynamic')
    environments = db.relationship('GeneratedEnvironment', backref='project', lazy='dynamic')
    versions = db.relationship('ProjectVersion', backref='project', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'status': self.status,
            'task_id': self.task_id,
            'error_message': self.error_message,
            'project_data': self.project_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'asset_count': len(self.assets),
            'script_count': self.scripts.count(),
            'environment_count': self.environments.count()
        }

class AssetCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # model, texture, script, environment
    meta_data = db.Column(JSON)  # Store additional data like prompt, parameters
    file_size = db.Column(db.Integer)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'file_path': self.file_path,
            'asset_type': self.asset_type,
            'meta_data': self.meta_data,
            'file_size': self.file_size,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GeneratedScript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    script_type = db.Column(db.String(50), nullable=False)  # lua, python, csharp
    content = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'script_type': self.script_type,
            'content': self.content,
            'prompt': self.prompt,
            'file_path': self.file_path,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GeneratedEnvironment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    environment_type = db.Column(db.String(50), nullable=False)
    environment_data = db.Column(JSON, nullable=False)  # Store full environment configuration
    prompt = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'environment_type': self.environment_type,
            'environment_data': self.environment_data,
            'prompt': self.prompt,
            'file_path': self.file_path,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProjectVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    snapshot_data = db.Column(JSON)  # Store complete project state
    is_current = db.Column(db.Boolean, default=False)
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'version_number': self.version_number,
            'description': self.description,
            'snapshot_data': self.snapshot_data,
            'is_current': self.is_current,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    meta_data = db.Column(JSON)  # Store additional context, actions taken, etc.
    
    # Optional project context
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'meta_data': self.meta_data,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WebhookEndpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    endpoint_url = db.Column(db.String(500), nullable=False, unique=True)
    secret_key = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    
    # Event types this webhook responds to
    event_types = db.Column(JSON)  # ['generation_complete', 'project_complete', etc.]
    
    # Configuration
    config = db.Column(JSON)  # Additional webhook configuration
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'endpoint_url': self.endpoint_url,
            'is_active': self.is_active,
            'event_types': self.event_types,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count
        }

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User preferences
    material_style_lock = db.Column(db.String(50))  # Locked material style
    preferred_lod_level = db.Column(db.String(20), default='medium')  # low, medium, high
    auto_generate_variations = db.Column(db.Boolean, default=False)
    auto_fix_roblox = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'material_style_lock': self.material_style_lock,
            'preferred_lod_level': self.preferred_lod_level,
            'auto_generate_variations': self.auto_generate_variations,
            'auto_fix_roblox': self.auto_fix_roblox
        }
