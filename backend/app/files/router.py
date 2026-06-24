from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from app.auth.service import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.devices.service import get_device
from app.files.sftp import delete_sftp_path, list_sftp_directory, make_sftp_directory, read_sftp_file, rename_sftp_path


router = APIRouter(prefix="/api/files", tags=["files"])


class PathRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class RenameRequest(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User:
    return get_current_user(request, db)


@router.get("/capabilities")
def capabilities():
    return {
        "sftp": ["list", "download", "upload"],
        "smb": ["planned"],
        "nfs": ["planned"],
        "transfers": "MVP transfer endpoints will copy file contents and ignore incompatible xattrs/ACLs by design.",
    }


@router.get("/{device_id}/list")
def list_files(
    device_id: int,
    path: str = Query(default="."),
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    return list_sftp_directory(device, path)


@router.post("/{device_id}/mkdir")
def make_directory(
    device_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    make_sftp_directory(device, payload.path)
    return {"ok": True}


@router.post("/{device_id}/rename")
def rename_path(
    device_id: int,
    payload: RenameRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    rename_sftp_path(device, payload.source, payload.destination)
    return {"ok": True}


@router.post("/{device_id}/delete")
def delete_path(
    device_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    delete_sftp_path(device, payload.path)
    return {"ok": True}


@router.get("/{device_id}/download")
def download_file(
    device_id: int,
    path: str = Query(min_length=1, max_length=4096),
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    filename, content = read_sftp_file(device, path)
    return StreamingResponse(
        content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
