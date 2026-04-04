import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getComplaints, getAdminComplaints, updateComplaintStatus } from '../api/client'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const CATEGORIES = ['', 'electricity', 'water_supply', 'sanitation', 'roads', 'public_services']
const PRIORITIES = ['', 'urgent', 'high', 'normal', 'low']
const STATUSES = ['', 'pending', 'in_progress', 'resolved', 'closed']
const DEPARTMENTS = ['', 'electricity_dept', 'water_dept', 'sanitation_dept', 'roads_dept', 'public_services_dept']
const PAGE_SIZE = 10

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

function CategoryBadge({ category }) {
  const map = {
    electricity: 'badge-electricity',
    water_supply: 'badge-water_supply',
    sanitation: 'badge-sanitation',
    roads: 'badge-roads',
    public_services: 'badge-public_services',
  }
  const cls = map[category?.toLowerCase()] || 'badge-normal'
  return <span className={`badge ${cls}`}>{formatLabel(category)}</span>
}

function StatusSelect({ complaint, onUpdate }) {
  const [updating, setUpdating] = useState(false)

  const handleChange = async (e) => {
    const newStatus = e.target.value
    setUpdating(true)
    try {
      await updateComplaintStatus(complaint.id, newStatus)
      toast.success('Status updated')
      onUpdate(complaint.id, newStatus)
    } catch {
      toast.error('Failed to update status')
    } finally {
      setUpdating(false)
    }
  }

  return (
    <select
      className="form-select"
      style={{ padding: '0.25rem 0.5rem', fontSize: '0.78rem', minWidth: '110px' }}
      value={complaint.status}
      onChange={handleChange}
      disabled={updating}
    >
      {STATUSES.filter(Boolean).map((s) => (
        <option key={s} value={s}>{formatLabel(s)}</option>
      ))}
    </select>
  )
}

export default function MyComplaintsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const isAdmin = user?.is_admin

  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({
    category: '', department: '', priority: '', status: '',
  })

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = {
        skip: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      }
      if (filters.category) params.category = filters.category
      if (filters.department) params.department = filters.department
      if (filters.priority) params.priority = filters.priority
      if (filters.status) params.status = filters.status

      const fn = isAdmin ? getAdminComplaints : getComplaints
      const res = await fn(params)
      const data = res.data
      if (Array.isArray(data)) {
        setComplaints(data)
        setTotal(data.length < PAGE_SIZE ? (page - 1) * PAGE_SIZE + data.length : page * PAGE_SIZE + 1)
      } else {
        setComplaints(data.items || data.complaints || [])
        setTotal(data.total || 0)
      }
    } catch (err) {
      toast.error('Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }, [page, filters, isAdmin])

  useEffect(() => { fetchData() }, [fetchData])

  const handleFilterChange = (e) => {
    setFilters((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setPage(1)
  }

  const clearFilters = () => {
    setFilters({ category: '', department: '', priority: '', status: '' })
    setPage(1)
  }

  const handleStatusUpdate = (id, newStatus) => {
    setComplaints((prev) =>
      prev.map((c) => (c.id === id ? { ...c, status: newStatus } : c))
    )
  }

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <div className="page-header">
        <h1>{isAdmin ? 'All Complaints' : 'My Complaints'}</h1>
        <p>
          {isAdmin
            ? 'Manage and update all submitted complaints.'
            : 'Track your submitted complaints and their status.'}
        </p>
      </div>

      {/* Filters */}
      <div className="filters-row">
        <div className="form-group">
          <label className="form-label">Category</label>
          <select name="category" className="form-select" value={filters.category} onChange={handleFilterChange}>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c ? formatLabel(c) : 'All'}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Department</label>
          <select name="department" className="form-select" value={filters.department} onChange={handleFilterChange}>
            {DEPARTMENTS.map((d) => <option key={d} value={d}>{d ? formatLabel(d) : 'All'}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Priority</label>
          <select name="priority" className="form-select" value={filters.priority} onChange={handleFilterChange}>
            {PRIORITIES.map((p) => <option key={p} value={p}>{p ? formatLabel(p) : 'All'}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Status</label>
          <select name="status" className="form-select" value={filters.status} onChange={handleFilterChange}>
            {STATUSES.map((s) => <option key={s} value={s}>{s ? formatLabel(s) : 'All'}</option>)}
          </select>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn btn-secondary btn-sm" onClick={clearFilters}>
            Clear Filters
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-center" style={{ padding: '3rem' }}>
            <div className="spinner" />
          </div>
        ) : complaints.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No complaints found.</p>
            {!isAdmin && (
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/')}>
                Submit a Complaint
              </button>
            )}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Department</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                  {isAdmin && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {complaints.map((c, idx) => (
                  <tr key={c.id}>
                    <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                      {(page - 1) * PAGE_SIZE + idx + 1}
                    </td>
                    <td style={{ maxWidth: '220px' }}>
                      <span
                        title={c.title}
                        style={{
                          display: 'block',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          fontWeight: 500,
                          color: '#1e293b',
                        }}
                      >
                        {c.title}
                      </span>
                    </td>
                    <td><CategoryBadge category={c.category} /></td>
                    <td style={{ fontSize: '0.82rem' }}>{formatLabel(c.department)}</td>
                    <td>
                      <span className={`badge badge-${c.priority}`}>{formatLabel(c.priority)}</span>
                    </td>
                    <td>
                      <span className={`badge badge-${c.status}`}>{formatLabel(c.status)}</span>
                    </td>
                    <td style={{ fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
                      {formatDate(c.created_at)}
                    </td>
                    {isAdmin && (
                      <td>
                        <StatusSelect complaint={c} onUpdate={handleStatusUpdate} />
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {!loading && complaints.length > 0 && (
        <div className="pagination">
          <button
            className="btn btn-secondary btn-sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Prev
          </button>
          <span className="page-info">Page {page}</span>
          <button
            className="btn btn-secondary btn-sm"
            disabled={complaints.length < PAGE_SIZE}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
