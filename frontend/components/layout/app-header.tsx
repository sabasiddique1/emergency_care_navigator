"use client"

import { MapPin, User, Settings as SettingsIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface AppHeaderProps {
  currentLocation?: string
  triageStatus?: "emergency" | "high" | "medium" | "low" | null
}

export function AppHeader({ currentLocation, triageStatus }: AppHeaderProps) {
  const getTriageBadgeVariant = (status?: string) => {
    switch (status) {
      case "emergency":
        return "emergency"
      case "high":
        return "warning"
      case "medium":
        return "default"
      case "low":
        return "success"
      default:
        return "outline"
    }
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-4 lg:px-6">
      <div className="flex flex-1 items-center gap-4">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            {currentLocation || "No location set"}
          </span>
        </div>
        {triageStatus && (
          <Badge variant={getTriageBadgeVariant(triageStatus)}>
            {triageStatus.toUpperCase()}
          </Badge>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <SettingsIcon className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  )
}

