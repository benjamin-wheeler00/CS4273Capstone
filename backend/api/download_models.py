# Used to bake the WhisperX model into the Docker image

import os
import sys
from pathlib import Path

# Add the backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from api.services.whisperx_transcriber import WhisperXTranscriber

token = os.getenv("HF_TOKEN") or Path("/run/secrets/hf_token").read_text()
token = token.strip()

if not token:
    raise RuntimeError("Hugging face token is empty")

os.environ["HF_TOKEN"] = token.strip()

WhisperXTranscriber().load_model()
