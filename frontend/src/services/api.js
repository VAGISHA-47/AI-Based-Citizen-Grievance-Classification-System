const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("jansetu_token") || "";

async function apiRequest(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
    ...options.headers,
  };
  const res = await fetch(BASE_URL + endpoint, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// AUTH
export const registerUser = (data) =>
  apiRequest("/auth/register", { method: "POST", body: JSON.stringify(data) });

export const loginUser = (data) =>
  apiRequest("/auth/login", { method: "POST", body: JSON.stringify(data) });

export const getMe = () => apiRequest("/auth/me");

// LOCATIONS (for officer login dropdowns)
export const getStates = () => apiRequest("/api/v1/locations/states");
export const getDistricts = (state_id) => apiRequest(`/api/v1/locations/districts?state_id=${state_id}`);
export const getAreas = (district_id) => apiRequest(`/api/v1/locations/areas?district_id=${district_id}`);
export const getWards = (area_id) => apiRequest(`/api/v1/locations/wards?area_id=${area_id}`);

// COMPLAINTS / GRIEVANCES
export const submitComplaint = (payload) =>
  apiRequest("/api/v1/complaints", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const submitGrievance = submitComplaint;

export const trackComplaint = (token) =>
  apiRequest(`/api/v1/complaints/${token}`);

export const getMyComplaints = () => apiRequest("/grievances/my");

// OFFICER
export const getAssignedComplaints = () => apiRequest("/officer/assigned");

export const resolveComplaint = (id, resolution) =>
  apiRequest(`/officer/${id}/resolve`, {
    method: "PATCH",
    body: JSON.stringify({ resolution }),
  });

export const getAnalytics = () => apiRequest("/officer/analytics/summary");
