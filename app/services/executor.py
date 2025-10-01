# app/services/executor.py
import logging, json
from io import BytesIO
from uuid import UUID
from ..models.job import JobPublishMessage, JobResultMessage
from ..clients.filestore import get_file, upload_json, upload_pdf
from ..clients.processor import run_redact, run_extract
from .callback import post_result

log = logging.getLogger(__name__)

def extract(message: JobPublishMessage, callback_url: str) -> None:
    """Detect PII, upload JSON, callback with JobResultMessage."""
    job_id = message.jobId
    try:
        stream = get_file(str(message.fileKey))
        try:
            results = run_extract(stream)  # list[dict]
        finally:
            try: stream.close()
            except Exception: pass

        pii_file_key = upload_json(results)
        if not pii_file_key:
            raise RuntimeError("upload_json returned no fileKey")

        result = JobResultMessage(
            pdfRedactionId=getattr(message, "pdfRedactionId", None),
            jobId=job_id,
            currentTenant=message.tenantName,
            fileKey=message.fileKey,
            piiFileKey=_as_uuid_or_none(pii_file_key),
            jobType=message.jobType,
            redactedFileKey=None,
            jobStatus="COMPLETED",
            error=None
        ).model_dump()

        post_result(callback_url, result)
        log.info("EXTRACT job %s completed -> pii=%s", job_id, pii_file_key)

    except Exception as e:
        result = JobResultMessage(
            pdfRedactionId=getattr(message, "pdfRedactionId", None),
            jobId=job_id,
            currentTenant=message.tenantName,
            fileKey=message.fileKey,
            piiFileKey=None,
            jobType=message.jobType,
            redactedFileKey=None,
            jobStatus="FAILED",
            error=str(e)
        ).model_dump()
        try:
            post_result(callback_url, result)
        finally:
            log.exception("EXTRACT job %s failed", job_id)

def redact(message: JobPublishMessage, callback_url: str) -> None:
    """Generate redacted PDF from (fileKey + piiFileKey), upload, callback with JobResultMessage."""
    job_id = message.jobId
    try:
        stream = get_file(str(message.fileKey))
        pii_stream = get_file(str(message.piiFileKey)) if message.piiFileKey else BytesIO(b"[]")
        try:
            redacted_file_path = run_redact(stream, pii_stream)  # temp path to PDF
        finally:
            try:
                stream.close()
                pii_stream.close()
            except Exception:
                pass

        with open(redacted_file_path, "rb") as f:
            redacted_key = upload_pdf(BytesIO(f.read()), filename=f"redacted_{job_id}.pdf")

        # cleanup temp file
        try:
            import os
            os.remove(redacted_file_path)
        except Exception:
            pass

        result = JobResultMessage(
            pdfRedactionId=getattr(message, "pdfRedactionId", None),
            jobId=job_id,
            currentTenant=message.tenantName,
            fileKey=message.fileKey,
            piiFileKey=message.piiFileKey,
            jobType=message.jobType,
            redactedFileKey=_as_uuid_or_none(redacted_key),
            jobStatus="COMPLETED",
            error=None
        ).model_dump()

        post_result(callback_url, result)
        log.info("REDACT job %s completed -> pii=%s redacted=%s", job_id, message.piiFileKey, redacted_key)

    except Exception as e:
        result = JobResultMessage(
            pdfRedactionId=getattr(message, "pdfRedactionId", None),
            jobId=job_id,
            currentTenant=message.tenantName,
            fileKey=message.fileKey,
            piiFileKey=message.piiFileKey,
            jobType=message.jobType,
            redactedFileKey=None,
            jobStatus="FAILED",
            error=str(e)
        ).model_dump()
        try:
            post_result(callback_url, result)
        finally:
            log.exception("REDACT job %s failed", job_id)

def _as_uuid_or_none(s: str):
    try:
        return UUID(str(s))
    except Exception:
        return None
