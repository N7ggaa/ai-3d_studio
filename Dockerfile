FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for some Python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files first for better caching
COPY app/ModelForge-1/requirements.txt /app/requirements.txt
COPY app/ModelForge-1/requirements_enhanced.txt /app/requirements_enhanced.txt

# Install Python dependencies with fallback strategy
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    (pip install --no-cache-dir -r /app/requirements_enhanced.txt || \
     (echo "Installing core packages individually..." && \
      pip install --no-cache-dir flask==3.1.0 flask-sqlalchemy==3.1.1 sqlalchemy==2.0.43 fastapi==0.112.2 uvicorn[standard]==0.30.6 && \
      pip install --no-cache-dir requests==2.32.3 pillow>=10.0.0 numpy>=1.24.0 opencv-python>=4.8.0))

# Copy the rest of the application
COPY app/ModelForge-1/ /app/

EXPOSE 5000

CMD ["python", "app.py"]