from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.database.models import Device, DeviceShare, Session, TransferJob, User  # noqa: F401
from app.database.migrations import run_startup_migrations
from app.database.session import Base, engine
from app.devices.router import router as devices_router
from app.files.router import router as files_router
from app.ssh.router import router as ssh_router
from app.transfers.router import router as transfers_router


logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)
run_startup_migrations()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(devices_router)
app.include_router(files_router)
app.include_router(ssh_router)
app.include_router(transfers_router)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "secret_configured": settings.has_persistent_secret,
        "app": settings.app_name,
    }
