from __future__ import annotations

from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    connection_type: str = Field(pattern="^(ssh_sftp|smb|nfs)$")
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    username: str = Field(default="", max_length=120)
    auth_method: str = Field(pattern="^(none|password|ssh_key)$")
    password: str | None = Field(default=None, max_length=4096)
    private_key: str | None = Field(default=None, max_length=20000)
    active: bool = True


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    host: str | None = Field(default=None, min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    username: str | None = Field(default=None, max_length=120)
    auth_method: str | None = Field(default=None, pattern="^(none|password|ssh_key)$")
    password: str | None = Field(default=None, max_length=4096)
    private_key: str | None = Field(default=None, max_length=20000)
    active: bool | None = None


class DeviceResponse(BaseModel):
    id: int
    name: str
    connection_type: str
    host: str
    port: int
    username: str
    auth_method: str
    active: bool

    model_config = {"from_attributes": True}


class DeviceTestResponse(BaseModel):
    ok: bool
    status: str
