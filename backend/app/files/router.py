from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from app.auth.service import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.devices.service import get_device, get_device_share
from app.files.smb import delete_smb_path, list_smb_directory, make_smb_directory, read_smb_file, rename_smb_path
from app.files.sftp import delete_sftp_path, list_sftp_directory, make_sftp_directory, read_sftp_file, rename_sftp_path


router = APIRouter(prefix="/api/files", tags=["files"])


class PathRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class RenameRequest(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User:
    return get_current_user(request, db)


def _list_target(target, path: str):
    if target.connection_type == "smb":
        return list_smb_directory(target, path)
    return list_sftp_directory(target, path)


def _mkdir_target(target, path: str) -> None:
    if target.connection_type == "smb":
        make_smb_directory(target, path)
        return
    make_sftp_directory(target, path)


def _rename_target(target, source: str, destination: str) -> None:
    if target.connection_type == "smb":
        rename_smb_path(target, source, destination)
        return
    rename_sftp_path(target, source, destination)


def _delete_target(target, path: str) -> None:
    if target.connection_type == "smb":
        delete_smb_path(target, path)
        return
    delete_sftp_path(target, path)


def _read_target(target, path: str):
    if target.connection_type == "smb":
        filename, raw_content = read_smb_file(target, path)
        import io

        return filename, io.BytesIO(raw_content)
    return read_sftp_file(target, path)


@router.get("/capabilities")
def capabilities():
    return {
        "sftp": ["list", "download", "upload"],
        "smb": ["list", "download", "mkdir", "rename", "delete"],
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
    return _list_target(device, path)


@router.get("/shares/{share_id}/list")
def list_share_files(
    share_id: int,
    path: str = Query(default="."),
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    share = get_device_share(db, user, share_id)
    return _list_target(share, path)


@router.post("/{device_id}/mkdir")
def make_directory(
    device_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    _mkdir_target(device, payload.path)
    return {"ok": True}


@router.post("/shares/{share_id}/mkdir")
def make_share_directory(
    share_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    share = get_device_share(db, user, share_id)
    _mkdir_target(share, payload.path)
    return {"ok": True}


@router.post("/{device_id}/rename")
def rename_path(
    device_id: int,
    payload: RenameRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    _rename_target(device, payload.source, payload.destination)
    return {"ok": True}


@router.post("/shares/{share_id}/rename")
def rename_share_path(
    share_id: int,
    payload: RenameRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    share = get_device_share(db, user, share_id)
    _rename_target(share, payload.source, payload.destination)
    return {"ok": True}


@router.post("/{device_id}/delete")
def delete_path(
    device_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    _delete_target(device, payload.path)
    return {"ok": True}


@router.post("/shares/{share_id}/delete")
def delete_share_path(
    share_id: int,
    payload: PathRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    share = get_device_share(db, user, share_id)
    _delete_target(share, payload.path)
    return {"ok": True}


@router.get("/{device_id}/download")
def download_file(
    device_id: int,
    path: str = Query(min_length=1, max_length=4096),
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    device = get_device(db, user, device_id)
    filename, content = _read_target(device, path)
    return StreamingResponse(
        content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/shares/{share_id}/download")
def download_share_file(
    share_id: int,
    path: str = Query(min_length=1, max_length=4096),
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    share = get_device_share(db, user, share_id)
    filename, content = _read_target(share, path)
    return StreamingResponse(
        content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
