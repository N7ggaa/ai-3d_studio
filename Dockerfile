FROM python:3.11-slim

WORKDIR /app

COPY app/ModelForge-1/ /app/

RUN pip install --no-cache-dir -r requirements_enhanced.txt

EXPOSE 5000

CMD ["python", "main.py"]