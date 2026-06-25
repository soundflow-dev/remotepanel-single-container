from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ParsedConnectionPath:
    connection_type: str
    host: str
    port: int
    normalized_url: str
    share: str | None = None
    remote_path: str = "/"


def parse_connection_path(connection_type: str, raw_path: str | None, fallback_host: str, fallback_port: int) -> ParsedConnectionPath:
    if connection_type == "ssh_sftp":
        return ParsedConnectionPath(
            connection_type=connection_type,
            host=fallback_host,
            port=fallback_port,
            normalized_url=raw_path or f"sftp://{fallback_host}:{fallback_port}",
        )

    if connection_type == "smb":
        return parse_smb_path(raw_path, fallback_host, fallback_port)

    if connection_type == "nfs":
        return parse_nfs_path(raw_path, fallback_host, fallback_port)

    raise ValueError("Unsupported connection type.")


def parse_smb_path(raw_path: str | None, fallback_host: str, fallback_port: int = 445) -> ParsedConnectionPath:
    value = (raw_path or "").strip()
    if value.startswith("\\\\"):
        parts = [part for part in re.split(r"\\+", value.strip("\\")) if part]
        host = parts[0] if parts else fallback_host
        share = parts[1] if len(parts) > 1 else None
        remote_path = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"
    else:
        if value.startswith("//"):
            value = f"smb:{value}"
        if value and "://" not in value:
            value = f"smb://{value}"
        parsed = urlparse(value or f"smb://{fallback_host}")
        host = parsed.hostname or fallback_host
        share_and_path = [part for part in parsed.path.split("/") if part]
        share = share_and_path[0] if share_and_path else None
        remote_path = "/" + "/".join(share_and_path[1:]) if len(share_and_path) > 1 else "/"

    normalized = f"smb://{host}"
    if share:
        normalized += f"/{share}"
        if remote_path != "/":
            normalized += remote_path
    return ParsedConnectionPath("smb", host, fallback_port or 445, normalized, share, remote_path)


def parse_nfs_path(raw_path: str | None, fallback_host: str, fallback_port: int = 2049) -> ParsedConnectionPath:
    value = (raw_path or "").strip()
    host = fallback_host
    export_path = "/"
    if value.startswith("nfs://"):
        parsed = urlparse(value)
        host = parsed.hostname or fallback_host
        export_path = parsed.path or "/"
    elif ":" in value:
        host_part, path_part = value.split(":", 1)
        host = host_part or fallback_host
        export_path = path_part or "/"
    elif value:
        host = value

    normalized = f"nfs://{host}{export_path}"
    return ParsedConnectionPath("nfs", host, fallback_port or 2049, normalized, None, export_path)
