from io import BytesIO
import json
from ..core.config import settings
from ..utils.http import http_client

def get_file(file_key: str) -> BytesIO:
    url = f"{settings.file_storage_url}{settings.file_get_endpoint}"
    with http_client() as c:
        r = c.get(
            url,
            params={"fileKey": file_key},
            auth=(settings.file_user, settings.file_pass.get_secret_value())
        )
        r.raise_for_status()
        return BytesIO(r.content)

def upload_json(json_obj: dict) -> str:
    url = f"{settings.file_storage_url}{settings.file_upload_endpoint}"
    files = {
        "file": ("result.json", BytesIO(json.dumps(json_obj).encode("utf-8"))),
        "fileDetails": (
            "fileDetails", json.dumps({
                    "projectName": "PdfRedaction",
                    "feature": "json"
                    }
            ),
            "application/json"
        )
    }
    with http_client() as c:
        r = c.post(url, files=files, auth=(settings.file_user, settings.file_pass.get_secret_value()))
        print()
        print()
        print(r.text)
        print()
        print()
        r.raise_for_status()
        # expect {"content":{"fileKey":"..."}}
        return r.json().get("content", {}).get("fileKey")
    
    

def upload_pdf(stream: BytesIO, filename: str = "redacted.pdf") -> str:
    """Upload a PDF artifact; returns storage fileKey (string)."""
    url = f"{settings.file_storage_url}{settings.file_upload_endpoint}"
    stream.seek(0)
    files = {
        "file": (filename, stream, "application/pdf"),
        "fileDetails": (
            "fileDetails",
            json.dumps({"projectName": "PdfRedaction", "feature": "pdf"}),
            "application/json",
        ),
    }
    with http_client() as c:
        r = c.post(
            url,
            files=files,
            auth=(settings.file_user, settings.file_pass.get_secret_value())
        )
        r.raise_for_status()
        return r.json().get("content", {}).get("fileKey")
