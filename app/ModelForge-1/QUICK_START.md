# ModelForge Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Start the App
```bash
python main.py
```
The app will be available at: **http://localhost:5000**

### 2. Generate Your First 3D Model
1. Go to **http://localhost:5000/generate**
2. Enter a prompt like: *"A futuristic spaceship with glowing engines"*
3. Click "Generate Model"
4. Wait for processing (usually 10-30 seconds)
5. Download your 3D model!

### 3. Try the AI Chat
1. Go to **http://localhost:5000/chat**
2. Ask: *"Generate a medieval castle"*
3. The AI will create the model automatically

## 🛠️ What's Fixed

### ✅ FBX Conversion Error
- **Problem**: `FBX exporter not available` error
- **Solution**: Added graceful fallback to OBJ format
- **Result**: Models generate successfully even without Blender

### ✅ Database Schema Issues
- **Problem**: Missing columns in database
- **Solution**: Recreated database with correct schema
- **Result**: All features work properly

### ✅ Redis Connection Issues
- **Problem**: App hanging on Redis connection
- **Solution**: Switched to memory broker by default
- **Result**: App starts instantly without external dependencies

## 🔒 Security Guardrails Active

- ✅ **File Upload Security**: Only safe image formats allowed
- ✅ **Size Limits**: 16MB maximum file size
- ✅ **SQL Injection Protection**: All queries use ORM
- ✅ **XSS Protection**: Template auto-escaping enabled
- ✅ **Path Traversal Protection**: Secure filename handling
- ✅ **Session Security**: Unique session IDs and timeouts

## 📁 Generated Files

Your 3D models will be saved in:
- **OBJ files**: `generated/model_[id].obj` (always available)
- **FBX files**: `generated/model_[id].fbx` (if Blender available)
- **Blend files**: `generated/model_[id].blend` (if Blender available)

## 🎯 Supported Prompts

Try these example prompts:
- *"A sleek sports car with aerodynamic design"*
- *"A magical treehouse in a fantasy forest"*
- *"A robot warrior with glowing blue eyes"*
- *"A cozy cottage with thatched roof"*
- *"A sci-fi space station orbiting Earth"*

## 🚨 Troubleshooting

### If the app won't start:
```bash
# Kill any existing processes
Stop-Process -Name "python" -Force

# Start fresh
python main.py
```

### If you get database errors:
```bash
# Recreate database
rm instance/app.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### If FBX conversion fails:
- The app will automatically use OBJ format
- Install Blender for FBX support (optional)
- **Windows users**: Run `python setup_blender.py` to automatically add Blender to PATH

## 📞 Need Help?

- Check the full documentation in `README.md`
- Review security details in `SECURITY.md`
- The app logs detailed information for debugging

---

**Ready to create amazing 3D models! 🎨**
