import logging
from fastapi import FastAPI
from .core import logging as logcfg
from .api.routes_jobs import router as jobs_router

logcfg  # import side-effects if you configure handlers here

def create_app() -> FastAPI:
    app = FastAPI(title="PdfRedaction Worker", version="0.1")
    app.include_router(jobs_router, prefix="")
    return app

app = create_app()
