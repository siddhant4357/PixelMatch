import os
import sys

# ── Monkey-patch: HfFolder was removed in huggingface_hub >= 1.0 but
# gradio 4.x oauth.py still imports it. Inject a stub before gradio loads.
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

import gradio as gr

# ── Register a dummy @spaces.GPU function so the HF Spaces 0.51.1 watchdog
# doesn't kill our process. On CPU-only spaces, spaces.GPU is a no-op
# decorator, so this has zero runtime cost.
try:
    import spaces

    @spaces.GPU(duration=0)
    def _noop():
        """Dummy function to satisfy the spaces watchdog on CPU spaces."""
        pass
except Exception:
    # spaces may not be available in all environments (e.g. local dev)
    pass

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

# Change working directory so relative paths in config.py resolve correctly
os.chdir(backend_path)

from main import app as fastapi_app

# Minimal Gradio status page
with gr.Blocks(title="PixelMatch API") as demo:
    gr.Markdown("# PixelMatch API 🚀")
    gr.Markdown("The backend API is running. Access the API docs at `/api/docs`.")

# Mount our FastAPI app into gradio's internal FastAPI at /api
demo.app.mount("/api", fastapi_app)

# Launch via gradio — sends the "ready" signal to the spaces watchdog
demo.launch(server_name="0.0.0.0", server_port=7860)
