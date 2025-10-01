# app/api/routes_jobs.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import HttpUrl
from ..models.job import JobPublishMessage
from ..services.executor import extract, redact
from ..core.security import basic_auth  # optional

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/extract-pii")
def extract_pii(
    body: JobPublishMessage,
    background: BackgroundTasks,
    callback_url: HttpUrl = Query(..., description="HTTPS endpoint"),
    _=Depends(basic_auth),  # remove if not needed
):
    # if not str(callback_url).lower().startswith("https://"):
    #     raise HTTPException(status_code=400, detail="callback_url must be HTTPS")
    background.add_task(extract, body, str(callback_url))
    return {"message": "Job accepted", "jobId": body.jobId, "callback_url": callback_url}

@router.post("/redact")
def redact_pdf(
    body: JobPublishMessage,
    background: BackgroundTasks,
    callback_url: HttpUrl = Query(..., description="HTTPS endpoint"),
    _=Depends(basic_auth),  # remove if not needed
):
    # if not str(callback_url).lower().startswith("https://"):
    #     raise HTTPException(status_code=400, detail="callback_url must be HTTPS")
    background.add_task(redact, body, str(callback_url))
    return {"message": "Job accepted", "jobId": body.jobId, "callback_url": callback_url}