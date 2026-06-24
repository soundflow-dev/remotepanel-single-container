const API_BASE = import.meta.env.VITE_API_BASE ?? "/api"

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  })

  if (response.status === 204) {
    return null
  }

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail ?? "Request failed")
  }
  return payload
}

export const api = {
  setupStatus: () => request("/auth/setup-status"),
  setup: (payload) => request("/auth/setup", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  logout: () => request("/auth/logout", { method: "POST" }),
  me: () => request("/auth/me"),
  listDevices: () => request("/devices"),
  createDevice: (payload) => request("/devices", { method: "POST", body: JSON.stringify(payload) }),
  updateDevice: (id, payload) => request(`/devices/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteDevice: (id) => request(`/devices/${id}`, { method: "DELETE" }),
  testDevice: (id) => request(`/devices/${id}/test`, { method: "POST" }),
  listFiles: (id, path = ".") => request(`/files/${id}/list?path=${encodeURIComponent(path)}`),
  mkdir: (id, path) => request(`/files/${id}/mkdir`, { method: "POST", body: JSON.stringify({ path }) }),
  renamePath: (id, source, destination) => request(`/files/${id}/rename`, { method: "POST", body: JSON.stringify({ source, destination }) }),
  deletePath: (id, path) => request(`/files/${id}/delete`, { method: "POST", body: JSON.stringify({ path }) }),
  transferSftp: (payload) => request("/transfers/sftp", { method: "POST", body: JSON.stringify(payload) }),
}
