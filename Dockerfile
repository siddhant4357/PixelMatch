FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    # InsightFace will look for models in the user's home directory
    INSIGHTFACE_HOME=/home/user/.insightface

WORKDIR /app

# Install system dependencies required by OpenCV and InsightFace
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user

# Set home to the user's home directory
ENV HOME=/home/user
ENV PATH="/home/user/.local/bin:${PATH}"

# Copy requirements and install
COPY --chown=user:user backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download the InsightFace buffalo_s model at BUILD time
RUN python -c " \
import os, urllib.request, zipfile; \
model_dir = os.path.join(os.environ['HOME'], '.insightface/models/buffalo_s'); \
os.makedirs(model_dir, exist_ok=True); \
print('Downloading buffalo_s model...'); \
urllib.request.urlretrieve('https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip', '/tmp/buffalo_s.zip'); \
with zipfile.ZipFile('/tmp/buffalo_s.zip', 'r') as z: z.extractall(model_dir); \
os.remove('/tmp/buffalo_s.zip'); \
print('Model ready at', model_dir); \
"

# Copy the rest of the backend code
COPY --chown=user:user backend/ .

EXPOSE 7860

# Start FastAPI
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
