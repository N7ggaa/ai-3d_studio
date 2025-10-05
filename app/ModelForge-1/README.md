# ModelForge - AI 3D Model Generator

A comprehensive AI-powered 3D model generation platform built with Flask, featuring procedural geometry generation, file conversion, and project management capabilities.

## 🚀 Features

### Core Functionality
- **AI-Powered 3D Model Generation** - Generate 3D models from text prompts
- **Reference Image Support** - Upload images to guide model generation
- **Multiple Format Export** - OBJ, FBX, and Blender file formats
- **Project Management** - Organize and manage your 3D assets
- **AI Chat Interface** - Interactive chat with AI for model requests
- **Asset Queue System** - Batch process multiple generation requests
- **Smart Variations** - Generate multiple variations of models
- **LOD Generation** - Create different detail levels for models
- **Roblox Integration** - Generate Lua scripts for Roblox Studio

### Technical Features
- **Modern Web Interface** - Bootstrap-based responsive design
- **Real-time Progress Tracking** - Monitor generation progress
- **File Conversion Pipeline** - Automatic format conversion
- **Database Management** - SQLAlchemy with SQLite/PostgreSQL support
- **Task Queue System** - Celery-based background processing
- **Caching System** - Intelligent asset caching
- **API Endpoints** - RESTful API for integration

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core programming language
- **Flask 3.1.2** - Web framework
- **SQLAlchemy 2.0.43** - Database ORM
- **Celery 5.5.3** - Task queue management
- **Trimesh 4.7.4** - 3D mesh processing
- **OpenAI API** - AI chat and script generation

### Frontend
- **Bootstrap 5** - UI framework
- **Feather Icons** - Icon library
- **JavaScript** - Interactive functionality
- **Custom CSS** - Styling and animations

### Dependencies
- **NumPy** - Numerical computing
- **Pillow** - Image processing
- **Plotly** - Data visualization
- **Requests** - HTTP client
- **Werkzeug** - WSGI utilities

## 📋 Prerequisites

### System Requirements
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Windows 10/11, macOS, or Linux

### Optional Dependencies
- **Blender** - For advanced file conversion (FBX, Blend)
- **Redis** - For production task queue (optional, uses memory broker by default)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ModelForge-1
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file (optional):
```env
# Database
DATABASE_URL=sqlite:///app.db

# Celery (optional)
CELERY_BROKER_URL=memory://
CELERY_RESULT_BACKEND=memory://

# OpenAI (optional, for AI chat)
OPENAI_API_KEY=your_openai_api_key

# Session
SESSION_SECRET=your-secret-key-here
```

### 4. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 5. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## 🎯 Usage Guide

### Generating 3D Models

1. **Navigate to Generate Page**
   - Go to `http://localhost:5000/generate`

2. **Enter Your Prompt**
   - Describe the 3D model you want to create
   - Be specific about style, materials, and details

3. **Upload Reference Image (Optional)**
   - Upload an image to guide the generation
   - Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP

4. **Configure Options**
   - **Material Style**: Choose from realistic, stylized, cartoon, etc.
   - **Generate Variations**: Create multiple versions
   - **Generate LOD**: Create different detail levels
   - **Fix for Roblox**: Generate Lua scripts

5. **Submit and Wait**
   - Click "Generate Model"
   - Monitor progress in real-time
   - Download when complete

### Using AI Chat

1. **Access Chat Interface**
   - Go to `http://localhost:5000/chat`

2. **Interact with AI**
   - Ask for model generation
   - Request modifications
   - Get suggestions and tips

3. **Direct Generation**
   - Use commands like "generate a spaceship"
   - AI will create the model automatically

### Managing Projects

1. **Create Projects**
   - Organize related models
   - Add descriptions and metadata

2. **Asset Management**
   - View generation history
   - Mark favorites
   - Download in various formats

3. **Batch Processing**
   - Use the queue system for multiple models
   - Monitor progress across all jobs

## 🔧 Configuration

### Database Configuration
```python
# SQLite (default)
DATABASE_URL=sqlite:///app.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/modelforge
```

### Celery Configuration
```python
# Memory broker (default, no Redis needed)
CELERY_BROKER_URL=memory://

# Redis broker (production)
CELERY_BROKER_URL=redis://localhost:6379/0
```

### File Storage
```python
# Upload folder
UPLOAD_FOLDER=uploads

# Generated files folder
GENERATED_FOLDER=generated

# Maximum file size (16MB)
MAX_CONTENT_LENGTH=16 * 1024 * 1024
```

## 🏗️ Architecture

### Project Structure
```
ModelForge-1/
├── ai_modules/           # AI integration modules
│   ├── chat_handler.py   # AI chat functionality
│   ├── script_generator.py # Lua script generation
│   └── environment_generator.py # Environment generation
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
├── templates/            # HTML templates
├── uploads/              # User uploads
├── generated/            # Generated 3D models
├── instance/             # Database files
├── app.py               # Main Flask application
├── models.py            # Database models
├── routes.py            # Web routes
├── tasks.py             # Celery tasks
├── model_generator.py   # 3D model generation
├── file_converter.py    # File format conversion
└── main.py              # Application entry point
```

### Database Schema
- **GenerationJob** - 3D model generation jobs
- **Project** - Project management
- **AssetCache** - Cached assets
- **GeneratedScript** - Generated Lua scripts
- **GeneratedEnvironment** - Environment data
- **ChatMessage** - AI chat messages
- **UserSession** - User session data
- **AssetQueue** - Batch processing queue
- **AIPack** - Themed asset packs

## 🔒 Security & Guardrails

### Input Validation
- **File Upload Security**: Whitelisted file types and size limits
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Template escaping and input sanitization
- **CSRF Protection**: Flask-WTF integration

### Rate Limiting
- **Request Throttling**: Limit generation requests per user
- **File Upload Limits**: Maximum file size enforcement
- **Session Management**: Secure session handling

### Error Handling
- **Graceful Degradation**: Fallback mechanisms for failed operations
- **User-Friendly Errors**: Clear error messages without exposing internals
- **Logging**: Comprehensive error logging for debugging

### Data Protection
- **Secure File Storage**: Isolated upload and generation directories
- **Database Security**: Connection pooling and prepared statements
- **Session Security**: Secure session configuration

## 🐛 Troubleshooting

### Common Issues

#### FBX Conversion Errors
```
Error: FBX exporter not available
```
**Solution**: Install Blender or use OBJ format as fallback

#### Database Errors
```
Error: table has no column named 'obj_path'
```
**Solution**: Recreate database with current schema
```bash
rm instance/app.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### Memory Issues
```
Error: Out of memory during generation
```
**Solution**: Reduce model complexity or increase system RAM

#### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port or kill existing process
```bash
python main.py --port 5001
```

### Performance Optimization

#### For Production
1. **Use PostgreSQL** instead of SQLite
2. **Configure Redis** for Celery
3. **Enable caching** with Redis
4. **Use Gunicorn** instead of Flask development server
5. **Configure Nginx** as reverse proxy

#### For Development
1. **Enable debug mode** for detailed error messages
2. **Use memory broker** for Celery (no Redis needed)
3. **Monitor logs** for performance issues

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Trimesh** - 3D mesh processing library
- **Flask** - Web framework
- **Bootstrap** - UI framework
- **OpenAI** - AI API integration
- **Blender Foundation** - 3D software for file conversion

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**ModelForge** - Empowering creators with AI-driven 3D model generation 🚀

---

## 🧩 ModelForge Bridge (FastAPI)

The ModelForge Bridge is a lightweight FastAPI service that serves generated variant metadata, thumbnails, and integrates with Roblox Open Cloud for uploading assets. It lives in `bridge_service.py`.

### Run the Bridge

Development with code reload but excluding heavy folders:

```powershell
python -m uvicorn bridge_service:app --host 127.0.0.1 --port 8765 --reload --reload-exclude generated --reload-exclude logs
```

Production-like (no reload):

```powershell
python -m uvicorn bridge_service:app --host 127.0.0.1 --port 8765
```

Optional path override if the repo was moved:

```powershell
$env:MODELFORGE_BASE = "c:\\path\\to\\ModelForge-original"
```

### Endpoints (pagination)

- `GET /variants?limit=200&order=score&offset=0&q=<text>&batch=<id>`
  - Returns a page of variants. Lower `score_total` is better. `offset` supports paging large result sets.
  - Optional filters:
    - `q` substring filter on `name`
    - `batch` exact match on batch id
- `GET /best?limit=50&offset=0&q=<text>&batch=<id>`
  - Best-scored variants with the same optional filters.
- `GET /variant/{name}`
  - Returns the manifest for a variant.
- `GET /thumb/{name}.png`
  - Returns the thumbnail for a variant.

### Roblox Open Cloud Upload

Set environment variables before running the server (personal account example):

```powershell
$env:ROBLOX_API_KEY = "<your_api_key>"
$env:ROBLOX_USER_ID = "1364141439"
```

Upload and wait for `asset_id`:

```powershell
irm -Method Post "http://127.0.0.1:8765/upload/<variantName>?poll_timeout=300"
```

Query parameters: `asset_type=Model`, `dry_run=true|false`, `poll=true|false`, `poll_timeout`, `poll_interval`.

### Development result cap

To keep responses tiny during development, set a global cap:

```powershell
$env:DEV_MAX_RESULTS = "500"   # 0 disables the cap (default)
```

### Cleanup Script

Use `cleanup_variants.py` to prune old/low-score variants and optionally remove OBJ files once FBX exists.

Examples:

```powershell
# Dry run: show what would be removed, keep top 500 globally
python cleanup_variants.py --keep 500

# Execute deletions, keep top 200 per batch and delete OBJ when FBX exists
python cleanup_variants.py --keep-per-batch 200 --delete-obj-after-fbx --yes

# If repo moved, specify base via env var
$env:MODELFORGE_BASE = "c:\\path\\to\\ModelForge-original"; python cleanup_variants.py --keep 1000 --yes
```

The script:
- Reads `logs/variants.jsonl`
- Collapses duplicates by name (latest wins)
- Sorts by `score_total` ascending
- Deletes manifest, chunked OBJ/FBX, and thumbnail for pruned variants (dry-run by default)

### Converter Script

Convert many OBJ files to FBX and optionally delete the OBJ after success using `convert_objs_to_fbx.py`:

```powershell
# Convert all OBJs under generated/ and delete OBJ after FBX
python convert_objs_to_fbx.py --glob "generated/**/*.obj" --delete-obj-after-fbx

# Convert a specific folder
python convert_objs_to_fbx.py --glob "generated/variants/auto/*.obj"

# Test with a small subset
python convert_objs_to_fbx.py --glob "generated/**/*.obj" --limit 50
```

### Advanced Cleanup

Remove huge/broken models with `cleanup_advanced.py`:

```powershell
# Dry run - see what would be removed
python cleanup_advanced.py --max-size-mb 10 --max-faces 50000

# Remove huge models and weird geometry
python cleanup_advanced.py --max-size-mb 5 --max-faces 10000 --detect-weird --yes

# Remove by score threshold
python cleanup_advanced.py --min-score 100 --yes
```

### Roblox Plugin Installation & Usage

#### Installation Method 1: Local Plugin (Recommended)
1. **Open Roblox Studio**
2. **Navigate to Plugins Folder:**
   - Click **Plugins** tab in ribbon
   - Click **Plugins Folder** button
   - Windows Explorer/Finder will open
3. **Install the Plugin:**
   - Create a new folder called `ModelForge`
   - Copy `RobloxPlugin.lua` into this folder
   - Rename it to `Main.lua`
4. **Restart Roblox Studio**
   - Close and reopen Studio
   - You'll see "ModelForge" button in the Plugins toolbar

#### Installation Method 2: Script Editor
1. Open Roblox Studio
2. Open **View** → **Output** and **View** → **Command Bar**
3. Create a new script in ServerScriptService
4. Paste the contents of `RobloxPlugin.lua`
5. Right-click script → "Save as Local Plugin"
6. Name it "ModelForge"

#### Prerequisites
- **Enable HTTP Requests:** Game Settings → Security → Allow HTTP Requests 
- **Start Bridge Service:**
  ```powershell
  # Start the ModelForge bridge API
  cd ModelForge-1
  python -m uvicorn bridge_service:app --host 127.0.0.1 --port 8765 --reload --reload-exclude generated --reload-exclude logs
  ```

#### Using the Plugin
1. **Open Gallery:** Click "ModelForge" button in toolbar
2. **Browse Models:** 
   - Scroll through generated variants
   - Use search box: type "castle" or "medieval"
   - Filter by batch: `batch:001` or `batch:fantasy`
3. **Preview Details:**
   - Click any thumbnail to see stats
   - View face count, chunks, quality score
4. **Upload to Roblox:**
   - Select a model
   - Click "Upload" button
   - Wait for upload completion
   - Model becomes available in your inventory
5. **Insert in Workspace:**
   - After upload completes
   - Click "Insert" to place at spawn
   - Or drag from inventory

#### Troubleshooting
- **"Connection Failed":** Ensure bridge is running on port 8765
- **"HTTP 403 Forbidden":** Enable HTTP requests in Game Settings
- **"Upload Failed":** Check Roblox API keys in environment variables
- **Plugin Not Showing:** Restart Studio after installation
- **Empty Gallery:** Check if variants exist in `generated/variants/auto/`
