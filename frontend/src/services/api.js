export const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem("jansetu_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const errorData = await response.json();
      message = errorData?.message || errorData?.detail || message;
    } catch {
      // Keep default message when the response body is not valid JSON.
    }

    throw new Error(message);
  }

  return response.json();
};

// AUTH
export const registerUser = (data) =>
  apiRequest("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) });

export const loginUser = (data) =>
  apiRequest("/api/v1/auth/login", { method: "POST", body: JSON.stringify(data) });

export const getMe = () => apiRequest("/auth/me");

export const getOfficerProfile = () => apiRequest("/api/v1/officers/me");

export const saveOfficerJurisdiction = (data) =>
  apiRequest("/api/v1/officers/me/jurisdiction", { method: "PATCH", body: JSON.stringify(data) });

// LOCATIONS
export const getStates = () => apiRequest("/api/v1/locations/states");

export const getDistricts = (stateId) => apiRequest(`/api/v1/locations/districts?state_id=${stateId}`);

export const getAreas = (districtId) => apiRequest(`/api/v1/locations/areas?district_id=${districtId}`);

export const getWards = (areaId) => apiRequest(`/api/v1/locations/wards?area_id=${areaId}`);

// GRIEVANCES
export const submitGrievance = (data) =>
  apiRequest("/api/v1/complaints", { method: "POST", body: JSON.stringify(data) });

export const trackComplaint = (token) =>
  apiRequest(`/api/v1/complaints/${token}`);

export const getCitizenComplaints = () =>
  apiRequest("/api/v1/complaints/my");

export const updateComplaintStatus = (id, status, note) =>
  apiRequest(`/api/v1/complaints/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status, note }),
  });

// OFFICER
export const getAssignedComplaints = () =>
  apiRequest("/api/v1/officers/me/queue");

export const resolveComplaint = (id, resolution) =>
  apiRequest(`/api/v1/complaints/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: resolution || "resolved", note: resolution || "Resolved" }),
  });

export const getAnalytics = () =>
  apiRequest("/api/v1/officers/analytics/summary");
