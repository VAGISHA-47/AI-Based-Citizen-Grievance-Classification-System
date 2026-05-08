export const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

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
  apiRequest("/auth/register", { method: "POST", body: JSON.stringify(data) });

export const loginUser = (data) =>
  apiRequest("/auth/login", { method: "POST", body: JSON.stringify(data) });

export const getMe = () => apiRequest("/auth/me");

// GRIEVANCES
export const submitGrievance = (formData) =>
  fetch(BASE_URL + "/grievances/", {
    method: "POST",
    headers: { Authorization: "Bearer " + (localStorage.getItem("jansetu_token") || "") },
    body: formData,
  }).then((r) => r.json());

export const trackComplaint = (token) =>
  apiRequest(`/grievances/track/${token}`);

export const getCitizenComplaints = () =>
  apiRequest("/grievances/my");

// OFFICER
export const getAssignedComplaints = () =>
  apiRequest("/officer/assigned");

export const resolveComplaint = (id, resolution) =>
  apiRequest(`/officer/${id}/resolve`, { method: "PATCH", body: JSON.stringify({ resolution }) });

export const getAnalytics = () =>
  apiRequest("/officer/analytics/summary");
