import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = (username, password) =>
  client.post('/auth/login', { username, password })

export const register = (username, email, password) =>
  client.post('/auth/register', { username, email, password })

export const getCurrentUser = () => client.get('/auth/me')

export const submitComplaint = (title, description) =>
  client.post('/complaints/', { title, description })

export const getComplaints = (params = {}) =>
  client.get('/complaints/', { params })

export const getComplaintById = (id) => client.get(`/complaints/${id}`)

export const updateComplaintStatus = (id, status) =>
  client.patch(`/complaints/${id}/status`, { status })

export const getAdminStats = () => client.get('/admin/stats')

export const getAdminComplaints = (params = {}) =>
  client.get('/admin/complaints', { params })

export default client
