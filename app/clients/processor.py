from io import BytesIO
import tempfile, os, json
from ..utils.proccess_pdf import extract_pii, redact

def run_extract(in_stream: BytesIO) -> list[dict]:
    in_stream.seek(0)
    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(in_stream.read())
        return extract_pii(path)  # list[dict]
    finally:
        try: os.remove(path)
        except Exception: pass

def run_redact(in_stream: BytesIO, pii_stream: BytesIO) -> str:
    """Return path to a temp redacted PDF."""
    in_stream.seek(0)
    pii_stream.seek(0)

    # Accept either a raw list or {"detections":[...]}
    entities = json.load(pii_stream)
    if isinstance(entities, dict) and "detections" in entities:
        entities = entities["detections"]
    pii_list = [e.get("word") for e in entities if isinstance(e, dict) and "word" in e]

    fd_pdf, path_pdf = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd_pdf, "wb") as f:
            f.write(in_stream.read())
        # redact and return the new path (caller will remove it after upload)
        return redact(path_pdf, pii_list)
    finally:
        try: os.remove(path_pdf)
        except Exception: pass
