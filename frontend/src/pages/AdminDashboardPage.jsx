import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import { getAdminStats, getAdminComplaints } from '../api/client'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const CATEGORY_COLORS = ['#3b82f6', '#10b981', '#f97316', '#8b5cf6', '#fbbf24']
const PRIORITY_COLORS = { urgent: '#dc2626', high: '#f97316', normal: '#3b82f6', low: '#94a3b8' }

function formatLabel(str) {
  if (!str) return '—'
  return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

export default function AdminDashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recentComplaints, setRecentComplaints] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/', { replace: true })
      return
    }

    const fetchAll = async () => {
      setLoading(true)
      try {
        const [statsRes, complaintsRes] = await Promise.all([
          getAdminStats(),
          getAdminComplaints({ limit: 10, skip: 0 }),
        ])
        setStats(statsRes.data)
        const data = complaintsRes.data
        setRecentComplaints(Array.isArray(data) ? data : data.items || data.complaints || [])
      } catch (err) {
        toast.error('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [user, navigate])

  if (!user?.is_admin) return null

  if (loading) {
    return (
      <div className="loading-center" style={{ minHeight: 'calc(100vh - 3.5rem)' }}>
        <div className="spinner" />
      </div>
    )
  }

  const categoryData = stats?.by_category
    ? Object.entries(stats.by_category).map(([name, value]) => ({ name: formatLabel(name), value }))
    : []

  const priorityData = stats?.by_priority
    ? Object.entries(stats.by_priority).map(([name, value]) => ({ name: formatLabel(name), value, fill: PRIORITY_COLORS[name] || '#94a3b8' }))
    : []

  const departmentData = stats?.by_department
    ? Object.entries(stats.by_department).map(([name, value]) => ({ name: formatLabel(name), value }))
    : []

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p>Overview of all citizen grievances and their classification.</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card" style={{ borderLeftColor: '#2563eb' }}>
          <div className="stat-value">{stats?.total ?? '—'}</div>
          <div className="stat-label">Total Complaints</div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#dc2626' }}>
          <div className="stat-value">{stats?.urgent ?? stats?.by_priority?.urgent ?? '—'}</div>
          <div className="stat-label">Urgent</div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#d97706' }}>
          <div className="stat-value">{stats?.pending ?? stats?.by_status?.pending ?? '—'}</div>
          <div className="stat-label">Pending</div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#16a34a' }}>
          <div className="stat-value">{stats?.resolved ?? stats?.by_status?.resolved ?? '—'}</div>
          <div className="stat-label">Resolved</div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Pie: By Category */}
        <div className="card">
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '1rem', color: '#334155' }}>
            Complaints by Category
          </h3>
          {categoryData.length === 0 ? (
            <p className="text-muted text-center">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={85}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Bar: By Priority */}
        <div className="card">
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '1rem', color: '#334155' }}>
            Complaints by Priority
          </h3>
          {priorityData.length === 0 ? (
            <p className="text-muted text-center">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={priorityData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" name="Complaints" radius={[4, 4, 0, 0]}>
                  {priorityData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Bar: By Department */}
        <div className="card">
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '1rem', color: '#334155' }}>
            Complaints by Department
          </h3>
          {departmentData.length === 0 ? (
            <p className="text-muted text-center">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={departmentData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" name="Complaints" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Recent Complaints Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #f1f5f9' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155' }}>
            Recent Complaints
          </h3>
        </div>
        {recentComplaints.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No complaints yet.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {recentComplaints.map((c, idx) => (
                  <tr key={c.id}>
                    <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{idx + 1}</td>
                    <td style={{ maxWidth: '200px' }}>
                      <span
                        title={c.title}
                        style={{
                          display: 'block',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          fontWeight: 500,
                        }}
                      >
                        {c.title}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${c.category}`}>{formatLabel(c.category)}</span>
                    </td>
                    <td>
                      <span className={`badge badge-${c.priority}`}>{formatLabel(c.priority)}</span>
                    </td>
                    <td>
                      <span className={`badge badge-${c.status}`}>{formatLabel(c.status)}</span>
                    </td>
                    <td style={{ fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
                      {formatDate(c.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
