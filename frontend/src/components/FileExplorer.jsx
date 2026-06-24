import { useEffect, useState } from "react"
import { Download, File, Folder, FolderPlus, RefreshCw, Trash2, X } from "lucide-react"

import { api } from "../api/client"

function joinPath(base, name) {
  if (!base || base === ".") return name
  return `${base.replace(/\/$/, "")}/${name}`
}

function formatSize(size) {
  if (size == null) return ""
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(1)} GB`
}

export function FileExplorer({ device, onClose }) {
  const [path, setPath] = useState(".")
  const [listing, setListing] = useState({ path: ".", parent: ".", entries: [] })
  const [message, setMessage] = useState("")
  const [busy, setBusy] = useState(false)

  async function load(nextPath = path) {
    setBusy(true)
    setMessage("")
    try {
      const result = await api.listFiles(device.id, nextPath)
      setListing(result)
      setPath(result.path)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    load(".")
  }, [device])

  async function createFolder() {
    const name = window.prompt("Folder name")
    if (!name) return
    await api.mkdir(device.id, joinPath(path, name))
    await load(path)
  }

  async function renameEntry(entry) {
    const nextName = window.prompt("New name", entry.name)
    if (!nextName || nextName === entry.name) return
    await api.renamePath(device.id, entry.path, joinPath(path, nextName))
    await load(path)
  }

  async function deleteEntry(entry) {
    if (!window.confirm(`Delete ${entry.name}?`)) return
    await api.deletePath(device.id, entry.path)
    await load(path)
  }

  function downloadEntry(entry) {
    window.location.href = `/api/files/${device.id}/download?path=${encodeURIComponent(entry.path)}`
  }

  return (
    <section className="fixed inset-0 z-20 flex flex-col bg-surface">
      <header className="flex flex-col gap-3 border-b border-line bg-panel px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-semibold text-ink">{device.name} files</h2>
          <p className="truncate text-xs text-muted">{path}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary px-3" onClick={() => load(path)} disabled={busy} title="Refresh">
            <RefreshCw size={17} aria-hidden="true" />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <button className="btn-secondary px-3" onClick={createFolder} title="Create folder">
            <FolderPlus size={17} aria-hidden="true" />
            <span className="hidden sm:inline">Folder</span>
          </button>
          <button className="btn-secondary px-3" onClick={onClose} title="Close files">
            <X size={17} aria-hidden="true" />
            <span className="hidden sm:inline">Close</span>
          </button>
        </div>
      </header>

      <div className="min-h-0 flex-1 overflow-auto p-3 sm:p-4">
        {message && <p className="mb-3 rounded-md border border-line bg-panel px-4 py-3 text-sm text-ink">{message}</p>}

        <div className="overflow-hidden rounded-lg border border-line bg-panel">
          <button className="flex w-full items-center gap-3 border-b border-line px-4 py-3 text-left text-sm text-ink hover:bg-surface" onClick={() => load(listing.parent)} disabled={path === "." || path === "/"}>
            <Folder size={18} aria-hidden="true" />
            ..
          </button>
          {listing.entries.map((entry) => (
            <div key={entry.path} className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 md:grid-cols-[1fr_120px_180px_auto]">
              <button className="flex min-w-0 items-center gap-3 text-left" onClick={() => entry.type === "directory" ? load(entry.path) : downloadEntry(entry)}>
                {entry.type === "directory" ? <Folder className="shrink-0 text-teal-300" size={19} aria-hidden="true" /> : <File className="shrink-0 text-muted" size={19} aria-hidden="true" />}
                <span className="truncate text-sm font-medium text-ink">{entry.name}</span>
              </button>
              <span className="hidden text-right text-xs text-muted md:block">{entry.type === "file" ? formatSize(entry.size) : ""}</span>
              <span className="hidden text-xs text-muted md:block">{entry.modified_at ? new Date(entry.modified_at).toLocaleString() : ""}</span>
              <div className="flex justify-end gap-2">
                {entry.type === "file" && (
                  <button className="btn-secondary min-h-9 px-2" onClick={() => downloadEntry(entry)} title="Download">
                    <Download size={15} aria-hidden="true" />
                  </button>
                )}
                <button className="btn-secondary min-h-9 px-2" onClick={() => renameEntry(entry)} title="Rename">
                  Rename
                </button>
                <button className="btn-danger min-h-9 px-2" onClick={() => deleteEntry(entry)} title="Delete">
                  <Trash2 size={15} aria-hidden="true" />
                </button>
              </div>
            </div>
          ))}
          {listing.entries.length === 0 && (
            <p className="px-4 py-8 text-center text-sm text-muted">Empty folder</p>
          )}
        </div>
      </div>
    </section>
  )
}
