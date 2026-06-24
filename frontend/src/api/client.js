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
  listShares: (deviceId) => request(`/devices/${deviceId}/shares`),
  createShare: (deviceId, payload) => request(`/devices/${deviceId}/shares`, { method: "POST", body: JSON.stringify(payload) }),
  updateShare: (id, payload) => request(`/devices/shares/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteShare: (id) => request(`/devices/shares/${id}`, { method: "DELETE" }),
  testShare: (id) => request(`/devices/shares/${id}/test`, { method: "POST" }),
  listFiles: (targetType, id, path = ".") => request(`/files/${targetType === "share" ? "shares/" : ""}${id}/list?path=${encodeURIComponent(path)}`),
  mkdir: (targetType, id, path) => request(`/files/${targetType === "share" ? "shares/" : ""}${id}/mkdir`, { method: "POST", body: JSON.stringify({ path }) }),
  renamePath: (targetType, id, source, destination) => request(`/files/${targetType === "share" ? "shares/" : ""}${id}/rename`, { method: "POST", body: JSON.stringify({ source, destination }) }),
  deletePath: (targetType, id, path) => request(`/files/${targetType === "share" ? "shares/" : ""}${id}/delete`, { method: "POST", body: JSON.stringify({ path }) }),
  downloadUrl: (targetType, id, path) => `/api/files/${targetType === "share" ? "shares/" : ""}${id}/download?path=${encodeURIComponent(path)}`,
  transferFiles: (payload) => request("/transfers/files", { method: "POST", body: JSON.stringify(payload) }),
  createTransferJob: (payload) => request("/transfers/jobs", { method: "POST", body: JSON.stringify(payload) }),
  listTransferJobs: () => request("/transfers/jobs"),
  cancelTransferJob: (id) => request(`/transfers/jobs/${id}/cancel`, { method: "POST" }),
  dismissTransferJob: (id) => request(`/transfers/jobs/${id}/dismiss`, { method: "POST" }),
}
