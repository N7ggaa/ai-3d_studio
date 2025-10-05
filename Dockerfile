FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY app/ModelForge-1/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ModelForge-1 application code
COPY app/ModelForge-1/ ./app/ModelForge-1/
COPY app.py ./app.py

# Expose port 5000
EXPOSE 5000

# Run the ModelForge-1 application
CMD ["python", "app/ModelForge-1/app.py"]