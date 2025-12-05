"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Activity, AlertTriangle, Clock, MapPin, ArrowRight, Loader2, RefreshCw, Building2 } from "lucide-react"
import Link from "next/link"
import { getPatientSessions, PatientSession } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { useToast } from "@/hooks/use-toast"

export default function DashboardPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [sessions, setSessions] = useState<PatientSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState({
    sessionsToday: 0,
    emergencyCases: 0,
    averageETA: 0,
    activeTriages: 0,
  })

  useEffect(() => {
    loadRecentActivity()
  }, [user])

  const loadRecentActivity = async () => {
    if (!user?.email) {
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      const data = await getPatientSessions(user.email)
      setSessions(data)

      // Calculate stats
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const todaySessions = data.filter(s => {
        if (!s.requested_at) return false
        const sessionDate = new Date(s.requested_at)
        return sessionDate >= today
      })

      const emergencyCases = data.filter(s => s.triage_level === "emergency").length
      const activeTriages = data.filter(s => 
        s.status === "PENDING_ACK" || s.status === "PENDING_APPROVAL" || s.status === "pending_approval"
      ).length

      setStats({
        sessionsToday: todaySessions.length,
        emergencyCases,
        averageETA: 15, // This would need to be calculated from actual ETA data
        activeTriages,
      })
    } catch (error) {
      console.error("Failed to load recent activity:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load recent activity",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimeAgo = (dateString?: string) => {
    if (!dateString) return "Unknown"
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? "minute" : "minutes"} ago`
    if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`
    return `${diffDays} ${diffDays === 1 ? "day" : "days"} ago`
  }

  const getTriageBadgeVariant = (level?: string) => {
    switch (level) {
      case "emergency":
        return "destructive"
      case "high":
        return "default"
      case "medium":
        return "secondary"
      case "low":
        return "outline"
      default:
        return "outline"
    }
  }

  const recentSessions = sessions.slice(0, 5) // Show latest 5
  return (
    <AppShell>
      <div className="space-y-6">
        {/* Hero Section */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">EmergencyCareNavigator</h1>
          <p className="text-muted-foreground">
            Multi-agent emergency care triage and facility routing system for faster decision-making and clinician handoff.
          </p>
        </div>

        {/* CTA */}
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-1">Start New Triage</h3>
                <p className="text-sm text-muted-foreground">
                  Begin a new emergency intake and triage assessment
                </p>
              </div>
              <Link href="/triage">
                <Button size="lg">
                  Start Triage
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Quick Stats</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Sessions Today</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.sessionsToday}</div>
                <p className="text-xs text-muted-foreground">+2 from yesterday</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Emergency Cases</CardTitle>
                <AlertTriangle className="h-4 w-4 text-destructive" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">{stats.emergencyCases}</div>
                <p className="text-xs text-muted-foreground">Require immediate attention</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average ETA</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.averageETA} min</div>
                <p className="text-xs text-muted-foreground">To nearest facility</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Triages</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.activeTriages}</div>
                <p className="text-xs text-muted-foreground">In progress</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold">Recent Activity</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={loadRecentActivity}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Recent Triage Sessions</CardTitle>
              <CardDescription>Latest emergency care assessments</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : recentSessions.length > 0 ? (
                <div className="space-y-4">
                  {recentSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                    >
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{session.patient_name || "Anonymous"}</span>
                          <Badge variant={getTriageBadgeVariant(session.triage_level)}>
                            {session.triage_level?.toUpperCase() || "UNKNOWN"}
                          </Badge>
                          {session.status && (
                            <Badge variant="outline" className="text-xs">
                              {session.status}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {session.location || "Unknown location"}
                          </div>
                          <div className="flex items-center gap-1">
                            <Building2 className="h-3 w-3" />
                            {session.facility_name || "Unknown facility"}
                          </div>
                          <div>{formatTimeAgo(session.requested_at)}</div>
                        </div>
                      </div>
                      <Link href={`/sessions?session=${session.session_id}`}>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No recent activity</p>
                  <p className="text-sm mt-1">Start a new triage to see activity here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}

