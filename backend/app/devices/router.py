from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session as DbSession

from app.auth.service import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.devices.schemas import DeviceCreate, DeviceResponse, DeviceTestResponse, DeviceUpdate
from app.devices.service import create_device, delete_device, get_device, list_devices, test_device_connection, update_device


router = APIRouter(prefix="/api/devices", tags=["devices"])


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User:
    return get_current_user(request, db)


@router.get("", response_model=list[DeviceResponse])
def devices(db: DbSession = Depends(get_db), user: User = Depends(current_user)):
    return list_devices(db, user)


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def add_device(payload: DeviceCreate, db: DbSession = Depends(get_db), user: User = Depends(current_user)):
    return create_device(db, user, payload)


@router.patch("/{device_id}", response_model=DeviceResponse)
def patch_device(device_id: int, payload: DeviceUpdate, db: DbSession = Depends(get_db), user: User = Depends(current_user)):
    return update_device(db, user, device_id, payload)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_device(device_id: int, db: DbSession = Depends(get_db), user: User = Depends(current_user)):
    delete_device(db, user, device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{device_id}/test", response_model=DeviceTestResponse)
def test_device(device_id: int, db: DbSession = Depends(get_db), user: User = Depends(current_user)):
    device = get_device(db, user, device_id)
    ok, message = test_device_connection(device)
    return DeviceTestResponse(ok=ok, status=message)
