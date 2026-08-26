import os
import sys

# ── Monkey-patch: HfFolder was removed in huggingface_hub >= 1.0 but
# gradio 4.x oauth.py still tries to import it. Provide a no-op stub
# so the import succeeds without affecting any real functionality.
import huggingface_hub as _hfh
if not hasattr(_hfh, "HfFolder"):
    class _HfFolderStub:
        @staticmethod
        def get_token():
            return None
        @staticmethod
        def save_token(token):
            pass
        @staticmethod
        def delete_token():
            pass
    _hfh.HfFolder = _HfFolderStub

# Now it is safe to import gradio
import gradio as gr

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

# Change working directory so relative paths in config.py resolve correctly
os.chdir(backend_path)

from main import app as fastapi_app

# Minimal status page — required so the HF Spaces watchdog finds a Gradio demo
with gr.Blocks(title="PixelMatch API") as demo:
    gr.Markdown("# PixelMatch API 🚀")
    gr.Markdown("The backend is running. API docs are available at `/docs`.")

# Mount the Gradio status page at /ui; FastAPI handles all other routes
app = gr.mount_gradio_app(fastapi_app, demo, path="/ui")

if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces routes external traffic to port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
