import os
import sys
import uvicorn

# Add the backend directory to the Python path so imports work correctly
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

# Change working directory to backend so relative paths in config.py work
os.chdir(backend_path)

# Import the FastAPI app — HF will serve this ASGI app on port 7860
from main import app  # noqa: F401

if __name__ == "__main__":
    # Hugging Face Spaces routes external traffic to port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
