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

# ── Key fix: mount our entire FastAPI app into gradio's internal FastAPI
# at the /api prefix.  demo.app is the FastAPI instance that gradio's own
# uvicorn server will serve — mounting here means all our routes are live
# without needing a separate uvicorn process.
demo.app.mount("/api", fastapi_app)

# ── CRITICAL: use demo.launch(), NOT uvicorn.run().
# The HF Spaces `spaces` watchdog listens for a "ready" signal that gradio
# sends during launch().  If we bypass launch() and call uvicorn directly,
# the watchdog never gets the signal and kills the process with
# "No @spaces.GPU function detected during startup".
demo.launch(server_name="0.0.0.0", server_port=7860)
