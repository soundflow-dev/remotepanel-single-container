# Jarvis Control Center

Self-hosted homelab control panel for managing devices, SSH/SFTP connections, file access, and remote actions from one web UI.

This repository is an early MVP scaffold. The first boot starts empty and shows the initial administrator setup screen.

## Current MVP

- FastAPI backend
- React + Tailwind frontend
- SQLite stored under `/data`
- Docker Compose deployment
- Initial admin setup lock
- Argon2id password hashing
- httpOnly cookie sessions
- Login, logout, and current-user endpoint
- Login rate limit with temporary user lockout
- Device credentials encrypted in SQLite using `APP_SECRET_KEY`
- Add, list, edit, delete, and test SSH/SFTP devices
- Web SSH terminal over backend WebSocket
- SFTP file explorer with multi-select actions
- SFTP to SFTP copy/move that copies file contents, preserves basic timestamps when possible, and ignores incompatible xattrs/ACLs
- Initial SMB share support for listing, downloading, creating folders, renaming, deleting, and copying/moving to or from SFTP/SMB
- Background transfer jobs with basic progress and recent history in the dashboard
- NFS connection records are accepted as groundwork, but browsing/mounting NFS is not implemented yet
- Responsive dark UI for desktop, tablet, and phone
- Transfer policy endpoint documenting the default "Transfers that just work" behavior

## Planned Next MVP Steps

- Full NFS browsing and transfers
- Transfer logs and cancellation controls
- 2FA/TOTP
- Multi-user permissions
- Plugins

## Security Defaults

Passwords are never stored in plain text. User passwords are hashed with Argon2id.

Device secrets are encrypted before being saved to SQLite. Set `APP_SECRET_KEY` to a long random value and keep it stable. If `APP_SECRET_KEY` is missing, the backend emits a clear warning and uses an ephemeral process key. That is useful for local testing only; encrypted credentials and sessions will not survive restarts.

Generate a secret:

```bash
openssl rand -base64 48
```

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8080
```

On first launch, create the administrator account. The setup route is locked after the first user exists.

## Adding Shares

SSH/SFTP devices use a host/IP, port, user, and password or private key.

SMB devices use a share path. Use the full share path when possible:

```text
smb://10.10.20.8/Media
\\10.10.20.8\Media
```

If the device has multiple shares, add each share as a separate connection for now. The stored SMB password is encrypted and is never sent back to the frontend after saving.

NFS paths can be saved in either form below, but NFS browsing is still planned:

```text
10.10.20.8:/mnt/pool/share
nfs://10.10.20.8/mnt/pool/share
```

## Ubuntu Server Install

1. Install Docker Engine and the Docker Compose plugin.
2. Clone this repository.
3. Create `.env` from `.env.example`.
4. Set `APP_SECRET_KEY` to a long random value.
5. Start the stack:

```bash
docker compose up -d --build
```

The app is available on `http://SERVER_IP:8080` unless you change `APP_PORT`.

## Unraid Install

Use this repository as a Compose project through the Docker Compose Manager plugin or a normal terminal workflow.

Recommended settings:

- Keep `APP_SECRET_KEY` in the Compose environment and do not rotate it casually.
- Map the frontend port with `APP_PORT`, for example `8080`.
- Keep the named `jarvis-data` volume, or replace it with an Unraid appdata bind mount such as `/mnt/user/appdata/jarvis-control-center:/data` for the backend service.

Example backend volume override:

```yaml
services:
  backend:
    volumes:
      - /mnt/user/appdata/jarvis-control-center:/data
```

## Transfer Philosophy

The file transfer design intentionally avoids rsync-style metadata failures by default.

Jarvis Control Center should copy file contents first, preserve basic dates when possible, preserve simple permissions only when safe, and silently ignore incompatible xattrs/ACLs such as Apple metadata streams:

- `user.DosStream.com.apple.quarantine:$DATA`
- `user.DosStream.com.apple.lastuseddate#PS:$DATA`
- `user.DosStream.com.apple.cscached:$DATA`
- `user.DOSATTRIB`

The goal is simple: transfers that just work.

## Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_SECRET_KEY=dev-secret DATA_DIR=./data uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE=http://localhost:8000/api` when running frontend and backend on separate dev ports.
