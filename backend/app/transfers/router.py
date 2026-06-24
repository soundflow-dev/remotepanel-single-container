from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from app.auth.service import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.devices.service import get_device
from app.transfers.files import transfer_file_paths


router = APIRouter(prefix="/api/transfers", tags=["transfers"])


class FileTransferRequest(BaseModel):
    source_device_id: int
    destination_device_id: int
    source_paths: list[str] = Field(min_length=1, max_length=200)
    destination_path: str = Field(default=".", min_length=1, max_length=4096)
    action: str = Field(pattern="^(copy|move)$")


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User:
    return get_current_user(request, db)


@router.get("/policy")
def transfer_policy():
    return {
        "name": "Transfers that just work",
        "defaults": [
            "copy file contents",
            "preserve basic timestamps when possible",
            "preserve basic permissions when safe",
            "ignore incompatible xattrs and ACLs",
            "never fail because of Apple metadata streams",
        ],
    }


@router.post("/sftp")
def transfer_sftp(
    payload: FileTransferRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    return transfer_files(payload, db, user)


@router.post("/files")
def transfer_files(
    payload: FileTransferRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(current_user),
):
    source_device = get_device(db, user, payload.source_device_id)
    destination_device = get_device(db, user, payload.destination_device_id)
    try:
        return transfer_file_paths(
            source_device=source_device,
            destination_device=destination_device,
            source_paths=payload.source_paths,
            destination_path=payload.destination_path,
            action=payload.action,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
