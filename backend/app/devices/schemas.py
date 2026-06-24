from __future__ import annotations

from pydantic import BaseModel, Field


class DeviceShareCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    connection_type: str = Field(pattern="^(smb|nfs)$")
    connection_url: str = Field(min_length=1, max_length=4096)
    port: int = Field(default=445, ge=1, le=65535)
    username: str = Field(default="", max_length=120)
    auth_method: str = Field(default="password", pattern="^(none|password)$")
    password: str | None = Field(default=None, max_length=4096)
    active: bool = True


class DeviceShareUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    connection_url: str | None = Field(default=None, min_length=1, max_length=4096)
    port: int | None = Field(default=None, ge=1, le=65535)
    username: str | None = Field(default=None, max_length=120)
    auth_method: str | None = Field(default=None, pattern="^(none|password)$")
    password: str | None = Field(default=None, max_length=4096)
    active: bool | None = None


class DeviceShareResponse(BaseModel):
    id: int
    device_id: int
    name: str
    connection_type: str
    connection_url: str
    host: str
    port: int
    username: str
    auth_method: str
    active: bool

    model_config = {"from_attributes": True}


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    connection_type: str = Field(default="machine", pattern="^(machine|ssh_sftp|smb|nfs)$")
    connection_url: str | None = Field(default=None, max_length=4096)
    host: str = Field(default="", max_length=255)
    port: int = Field(ge=1, le=65535)
    username: str = Field(default="", max_length=120)
    auth_method: str = Field(pattern="^(none|password|ssh_key)$")
    password: str | None = Field(default=None, max_length=4096)
    private_key: str | None = Field(default=None, max_length=20000)
    active: bool = True


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    host: str | None = Field(default=None, max_length=255)
    connection_url: str | None = Field(default=None, max_length=4096)
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
    connection_url: str | None
    host: str
    port: int
    username: str
    auth_method: str
    active: bool
    shares: list[DeviceShareResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DeviceTestResponse(BaseModel):
    ok: bool
    status: str
