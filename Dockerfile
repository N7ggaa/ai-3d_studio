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
COPY app/ModelForge-1/requirements.txt /app/
COPY app/ModelForge-1/requirements_enhanced.txt /app/

# Install base requirements first
RUN pip install --no-cache-dir -r requirements.txt

# Then install enhanced requirements (which includes base requirements via -r)
RUN pip install --no-cache-dir -r requirements_enhanced.txt

# Copy the rest of the application
COPY app/ModelForge-1/. /app/

EXPOSE 5000

CMD ["python", "app.py"]