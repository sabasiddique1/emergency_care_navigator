// API base URL
// - In development, set NEXT_PUBLIC_API_URL to "http://localhost:8000"
// - In production (Vercel), leave it unset so it defaults to empty string (same-origin)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Helper function to build API URLs
function buildApiUrl(path: string): string {
  // Remove leading slash from path if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  if (API_BASE_URL) {
    // If API_BASE_URL is set, use it (development)
    return `${API_BASE_URL}/${cleanPath}`;
  } else {
    // In production, use relative path (same-origin)
    return `/${cleanPath}`;
  }
}

// Helper function to build API URLs with query parameters
function buildApiUrlWithQuery(path: string, params?: Record<string, string>): string {
  const baseUrl = buildApiUrl(path);
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }
  
  // Build query string manually for better compatibility
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      queryParams.append(key, value);
    }
  });
  
  const queryString = queryParams.toString();
  return queryString ? `${baseUrl}?${queryString}` : baseUrl;
}

export interface IntakeAnswers {
  name?: string;
  location_query: string;
  symptoms: string[];
  unconscious?: boolean;
  breathing_difficulty?: boolean;
  chest_pain?: boolean;
  stroke_signs?: boolean;
  major_bleeding?: boolean;
  severe_allergy?: boolean;
  injury_trauma?: boolean;
  pregnancy?: boolean;
}

export interface TriageResult {
  level: 'emergency' | 'high' | 'medium' | 'low';
  reason: string;
  recommended_action: string;
  safety_note: string;
}

export interface Facility {
  name: string;
  address: string;
  lat: number;
  lon: number;
  kind: string;
  distance_km?: number;
  eta_minutes?: number;
  source: string;
}

export interface BookingState {
  request_type?: 'alert' | 'appointment';
  status: 'not_started' | 'PENDING_ACK' | 'ACKNOWLEDGED' | 'PENDING_APPROVAL' | 'CONFIRMED' | 'REJECTED' | 'pending_approval' | 'confirmed' | 'rejected' | 'failed' | 'skipped';
  facility_name?: string;
  requested_at?: string;
  approved_at?: string;
  acknowledged_at?: string;
  note?: string;
  session_id?: string;
  patient_name?: string;
  triage_level?: string;
}

export interface Recommendation {
  triage: TriageResult;
  top_choices: Facility[];
  route_notes: string;
  handoff_packet: string;
  booking_status: string;
  booking?: BookingState;
  session_id?: string;
}

export interface MemoryBank {
  preferred_city?: string;
  last_facility_used?: string;
  health_conditions?: string[];
}

export async function processIntake(intake: IntakeAnswers, patientEmail?: string): Promise<Recommendation> {
  const url = buildApiUrlWithQuery('api/intake', patientEmail ? { patient_email: patientEmail } : undefined);
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(intake),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process intake');
  }

  return response.json();
}

export async function getBookingStatus(sessionId: string): Promise<{ session_id: string; booking: BookingState; status: string }> {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(buildApiUrl(`api/booking/status/${sessionId}`), {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to get booking status');
  }

  return response.json();
}

export async function ackAlert(sessionId: string): Promise<BookingState> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(buildApiUrl(`api/booking/ack-alert/${sessionId}`), {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to acknowledge alert');
  }

  return response.json();
}

export async function approveAppointment(sessionId: string): Promise<BookingState> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(buildApiUrl(`api/booking/approve-appointment/${sessionId}`), {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to approve appointment');
  }

  return response.json();
}

// Legacy function - routes to appropriate endpoint
export async function approveBooking(sessionId: string): Promise<BookingState> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(buildApiUrl(`api/booking/approve/${sessionId}`), {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to approve booking');
  }

  return response.json();
}

export async function getHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(buildApiUrl('api/health'));
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
}

export async function getMemory(): Promise<MemoryBank> {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(buildApiUrl('api/memory'), {
    headers,
  });
  if (!response.ok) {
    throw new Error('Failed to get memory');
  }
  return response.json();
}

export async function updateMemory(memory: MemoryBank): Promise<{ status: string; memory: MemoryBank }> {
  const response = await fetch(buildApiUrl('api/memory'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(memory),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update memory');
  }
  return response.json();
}

export async function addHealthCondition(condition: string): Promise<{ status: string; memory: MemoryBank }> {
  const response = await fetch(buildApiUrl('api/memory/health-conditions'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ condition }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to add health condition');
  }
  return response.json();
}

export async function removeHealthCondition(condition: string): Promise<{ status: string; memory: MemoryBank }> {
  const response = await fetch(buildApiUrl(`api/memory/health-conditions/${encodeURIComponent(condition)}`), {
    method: 'DELETE',
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to remove health condition');
  }
  return response.json();
}

export interface DocumentUploadResponse {
  status: string;
  filename: string;
  extracted_conditions: string[];
  message: string;
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(buildApiUrl('api/documents/upload'), {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
}

// Authentication APIs
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'patient' | 'hospital_staff';
  facility_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role: 'patient' | 'hospital_staff';
  facility_name?: string;
}

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
}

export function removeAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
}

export function getStoredUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function setStoredUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('user', JSON.stringify(user));
}

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(buildApiUrl('api/auth/login'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  setStoredUser(data.user);
  return data;
}

export async function register(userData: RegisterRequest): Promise<AuthResponse> {
  const response = await fetch(buildApiUrl('api/auth/register'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  setStoredUser(data.user);
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const token = getAuthToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(buildApiUrl('api/auth/me'), {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    removeAuthToken();
    throw new Error('Authentication failed');
  }

  const user = await response.json();
  setStoredUser(user);
  return user;
}

export function logout(): void {
  removeAuthToken();
}

// Patient Requests APIs
export interface PatientRequest {
  id: string;
  session_id: string;
  facility_name: string;
  patient_name: string;
  triage_level: string;
  request_type: 'alert' | 'appointment';
  status: string;
  requested_at: string;
  approved_at?: string;
  acknowledged_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
  handoff_packet?: string;
  eta_minutes?: number;
  symptoms?: string[];
  location?: string;
}

export interface PendingRequestsResponse {
  count: number;
  requests: PatientRequest[];
  requested_hospitals: string[];
}

export async function getPatientRequests(patientEmail?: string): Promise<PatientRequest[]> {
  const url = buildApiUrlWithQuery('api/patient/requests', patientEmail ? { patient_email: patientEmail } : undefined);
  
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to get patient requests');
  }

  return response.json();
}

export async function getPendingRequests(patientEmail?: string): Promise<PendingRequestsResponse> {
  const url = buildApiUrlWithQuery('api/patient/requests/pending', patientEmail ? { patient_email: patientEmail } : undefined);
  
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to get pending requests');
  }

  return response.json();
}

// Session APIs
export interface SessionDetails {
  session_id: string;
  intake: any;
  triage: any;
  recommendation: any;
  booking: BookingState;
}

export interface PatientSession {
  session_id: string;
  patient_name: string;
  location: string;
  triage_level: string;
  facility_name: string;
  request_type: string;
  status: string;
  requested_at: string;
  booking_status: string;
}

export async function getSessionDetails(sessionId: string): Promise<SessionDetails> {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(buildApiUrl(`api/sessions/${sessionId}`), {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to get session details');
  }

  return response.json();
}

export async function getPatientSessions(patientEmail?: string): Promise<PatientSession[]> {
  const url = buildApiUrlWithQuery('api/sessions', patientEmail ? { patient_email: patientEmail } : undefined);
  
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to get patient sessions');
  }

  return response.json();
}

export function createAuthenticatedFetch() {
  return async (url: string, options: RequestInit = {}) => {
    const token = getAuthToken();
    const headers = new Headers(options.headers);
    
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    return fetch(url, {
      ...options,
      headers,
    });
  };
}

// Hospital Panel APIs
export interface HospitalBooking {
  id: string;
  session_id: string;
  facility_name: string;
  patient_name: string;
  triage_level: string;
  request_type?: 'alert' | 'appointment';
  status: 'pending_approval' | 'confirmed' | 'rejected' | 'PENDING_ACK' | 'ACKNOWLEDGED' | 'PENDING_APPROVAL' | 'CONFIRMED' | 'REJECTED';
  requested_at: string;
  approved_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
  handoff_packet?: string;
  eta_minutes?: number;
  symptoms?: string[];
  location?: string;
}

export interface HospitalFacility {
  name: string;
  pending_bookings: number;
  total_bookings: number;
}

export async function getHospitalFacilities(): Promise<HospitalFacility[]> {
  const response = await fetch(buildApiUrl('api/hospital/facilities'));
  if (!response.ok) {
    throw new Error('Failed to get hospital facilities');
  }
  return response.json();
}

export async function getHospitalBookings(facilityName: string, status?: string): Promise<HospitalBooking[]> {
  const url = buildApiUrlWithQuery(`api/hospital/bookings/${encodeURIComponent(facilityName)}`, status ? { status } : undefined);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to get hospital bookings');
  }
  return response.json();
}

export async function rejectBooking(sessionId: string, reason?: string): Promise<{ status: string; session_id: string; reason?: string }> {
  const response = await fetch(buildApiUrl(`api/booking/reject/${sessionId}`), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to reject booking');
  }
  return response.json();
}
