# app/models/job.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from uuid import UUID

class JobPublishMessage(BaseModel):
    pdfRedactionId: Optional[int] = None
    jobId: int
    fileKey: UUID
    piiFileKey: Optional[UUID] = None
    jobType: str
    tenantName: str
    tenantHeaderName: str

class JobResultMessage(BaseModel):
    # richer result resembling your Java class
    pdfRedactionId: int
    jobId: int
    currentTenant: str
    fileKey: Optional[UUID] = str
    jobType: str
    piiFileKey: Optional[UUID] = None
    redactedFileKey: Optional[UUID] = None
    jobStatus: str  # COMPLETED | FAILED
    error: Optional[str] = None
