"use client"

import { AppSidebar } from "./app-sidebar"
import { AppHeader } from "./app-header"
import { ReactNode } from "react"

interface AppShellProps {
  children: ReactNode
  currentLocation?: string
  triageStatus?: "emergency" | "high" | "medium" | "low" | null
}

export function AppShell({ children, currentLocation, triageStatus }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <div className="lg:pl-64">
        <AppHeader currentLocation={currentLocation} triageStatus={triageStatus} />
        <main className="p-4 lg:p-6">{children}</main>
      </div>
    </div>
  )
}

