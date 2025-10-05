# Installing Enhanced ModelForge Dependencies

## Quick Install (Windows PowerShell)

### Step 1: Open PowerShell in the ModelForge-1 directory
```powershell
cd c:\Users\dell\Downloads\ModelForge-original\ModelForge-1
```

### Step 2: Install the enhanced requirements
```powershell
pip install -r requirements_enhanced.txt
```

### Step 3: If you get errors, install dependencies one by one:
```powershell
# Core dependencies
pip install yt-dlp opencv-python

# 3D processing
pip install trimesh scipy scikit-image

# Video/Image processing  
pip install Pillow imageio ffmpeg-python

# Advanced mesh operations
pip install pymeshlab meshio psutil
```

### Step 4: Verify installation
```powershell
python -c "import cv2, yt_dlp, trimesh; print('✓ All enhanced dependencies installed!')"
```

## Troubleshooting

### If yt-dlp fails:
```powershell
# Update pip first
python -m pip install --upgrade pip
# Then retry
pip install yt-dlp
```

### If opencv-python fails:
```powershell
# Install pre-built wheel
pip install opencv-python-headless
```

### If trimesh fails:
```powershell
# Install without optional dependencies
pip install trimesh
```

## Test the Enhanced Features
```powershell
# Run the demo
python demo_enhanced_generation.py
```
