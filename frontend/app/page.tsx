"use client"

import { AppShell } from "@/components/layout/app-shell"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Activity, AlertTriangle, Clock, MapPin, ArrowRight } from "lucide-react"
import Link from "next/link"

// Mock data
const stats = {
  sessionsToday: 12,
  emergencyCases: 3,
  averageETA: 15,
  activeTriages: 2,
}

const recentSessions = [
  {
    id: "1",
    patient: "John Doe",
    location: "Karachi, Pakistan",
    triageLevel: "emergency" as const,
    timestamp: "2 hours ago",
    facility: "Aga Khan Hospital",
  },
  {
    id: "2",
    patient: "Anonymous",
    location: "Lahore, Pakistan",
    triageLevel: "high" as const,
    timestamp: "4 hours ago",
    facility: "Shaukat Khanum",
  },
  {
    id: "3",
    patient: "Jane Smith",
    location: "Islamabad, Pakistan",
    triageLevel: "medium" as const,
    timestamp: "6 hours ago",
    facility: "PIMS",
  },
]

export default function DashboardPage() {
  return (
    <ProtectedRoute>
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
          <h2 className="text-2xl font-semibold mb-4">Recent Activity</h2>
          <Card>
            <CardHeader>
              <CardTitle>Recent Triage Sessions</CardTitle>
              <CardDescription>Latest emergency care assessments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{session.patient}</span>
                        <Badge
                          variant={
                            session.triageLevel === "emergency"
                              ? "emergency"
                              : session.triageLevel === "high"
                              ? "warning"
                              : "default"
                          }
                        >
                          {session.triageLevel.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {session.location}
                        </div>
                        <div>{session.timestamp}</div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Facility: {session.facility}
                      </div>
                    </div>
                    <Link href={`/triage?session=${session.id}`}>
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
    </ProtectedRoute>
  )
}

