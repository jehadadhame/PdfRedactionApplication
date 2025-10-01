from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .config import settings

security = HTTPBasic()

def basic_auth(creds: HTTPBasicCredentials = Depends(security)):
    if creds.username != settings.basic_user or creds.password != settings.basic_pass.get_secret_value():
        raise HTTPException(status_code=401, detail="Unauthorized")
