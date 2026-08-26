import os
import sys
import uvicorn
import gradio as gr

# Add the backend directory to the Python path so imports work correctly
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

# Change working directory to backend so relative paths in config.py work
os.chdir(backend_path)

from main import app as fastapi_app

# Create a minimal Gradio interface
with gr.Blocks(title="PixelMatch API") as demo:
    gr.Markdown("# PixelMatch API is running!")
    gr.Markdown("The backend is successfully hosted and ready to accept API requests.")

# Mount the FastAPI app to the Gradio app
# Hugging Face Spaces (Gradio SDK) will automatically look for 'app'
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    # Hugging Face Spaces routes traffic to port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
