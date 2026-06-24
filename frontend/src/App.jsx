import React, { useEffect, useState } from "react"
import { createRoot } from "react-dom/client"

import "./styles.css"
import { api } from "./api/client"
import { Shell } from "./components/Shell"
import { DashboardPage } from "./pages/DashboardPage"
import { LoginPage } from "./pages/LoginPage"
import { SetupPage } from "./pages/SetupPage"

export default function App() {
  const [loading, setLoading] = useState(true)
  const [setupStatus, setSetupStatus] = useState(null)
  const [user, setUser] = useState(null)

  useEffect(() => {
    async function boot() {
      const status = await api.setupStatus()
      setSetupStatus(status)
      if (!status.setup_required) {
        try {
          setUser(await api.me())
        } catch {
          setUser(null)
        }
      }
      setLoading(false)
    }
    boot().catch(() => setLoading(false))
  }, [])

  async function logout() {
    await api.logout()
    setUser(null)
  }

  if (loading) {
    return <main className="grid min-h-screen place-items-center bg-surface text-sm text-muted">Loading...</main>
  }

  if (setupStatus?.setup_required) {
    return <SetupPage status={setupStatus} onReady={(createdUser) => {
      setSetupStatus({ ...setupStatus, setup_required: false })
      setUser(createdUser)
    }} />
  }

  if (!user) {
    return <LoginPage onReady={setUser} />
  }

  return (
    <Shell user={user} onLogout={logout}>
      <DashboardPage />
    </Shell>
  )
}

createRoot(document.getElementById("root")).render(<App />)
