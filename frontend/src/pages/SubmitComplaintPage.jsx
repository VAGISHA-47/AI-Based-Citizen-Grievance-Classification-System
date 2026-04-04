import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitComplaint } from '../api/client'
import toast from 'react-hot-toast'

function getCategoryClass(category) {
  const map = {
    electricity: 'badge-electricity',
    water_supply: 'badge-water_supply',
    sanitation: 'badge-sanitation',
    roads: 'badge-roads',
    public_services: 'badge-public_services',
  }
  return map[category?.toLowerCase()] || 'badge-normal'
}

function formatLabel(str) {
  if (!str) return '—'
  return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function SubmitComplaintPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', description: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) {
      setError('Title is required.')
      return
    }
    if (form.description.trim().length < 20) {
      setError('Description must be at least 20 characters.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await submitComplaint(form.title.trim(), form.description.trim())
      setResult(res.data)
      toast.success('Complaint submitted successfully!')
    } catch (err) {
      const detail = err.response?.data?.detail
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(', ')
        : detail || 'Failed to submit complaint. Please try again.'
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setForm({ title: '', description: '' })
    setError('')
  }

  if (result) {
    return (
      <div className="container" style={{ padding: '2rem 1rem', maxWidth: '640px' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '2rem' }}>✅</span>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#14532d' }}>
                Complaint Submitted
              </h2>
              <p className="text-muted">Your complaint has been classified automatically.</p>
            </div>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155', marginBottom: '0.75rem' }}>
              {result.title}
            </p>
            <div className="result-item">
              <span className="result-label">Category</span>
              <span className={`badge ${getCategoryClass(result.category)}`}>
                {formatLabel(result.category)}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Department</span>
              <span className="result-value">{formatLabel(result.department)}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Priority</span>
              <span className={`badge badge-${result.priority}`}>
                {formatLabel(result.priority)}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Sentiment Score</span>
              <span className="result-value">
                {result.sentiment_score != null
                  ? `${(result.sentiment_score * 100).toFixed(1)}%`
                  : '—'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Confidence Score</span>
              <span className="result-value">
                {result.confidence_score != null
                  ? `${(result.confidence_score * 100).toFixed(1)}%`
                  : '—'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Status</span>
              <span className={`badge badge-${result.status || 'pending'}`}>
                {formatLabel(result.status || 'pending')}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button className="btn btn-secondary" onClick={handleReset}>
              Submit Another
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/complaints')}>
              View My Complaints
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ padding: '2rem 1rem', maxWidth: '640px' }}>
      <div className="page-header">
        <h1>Submit a Complaint</h1>
        <p>Describe your grievance and our AI will classify it automatically.</p>
      </div>

      <div className="card">
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="title">Title <span style={{ color: '#dc2626' }}>*</span></label>
            <input
              id="title"
              name="title"
              type="text"
              className="form-control"
              placeholder="Brief summary of your complaint"
              value={form.title}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="description">
              Description <span style={{ color: '#dc2626' }}>*</span>
            </label>
            <textarea
              id="description"
              name="description"
              className="form-control"
              placeholder="Describe your complaint in detail (minimum 20 characters)…"
              rows={5}
              value={form.description}
              onChange={handleChange}
            />
            <p className="text-muted" style={{ fontSize: '0.78rem', marginTop: '0.25rem' }}>
              Supports English and Indian regional languages. Your complaint will be automatically classified.
            </p>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '0.65rem', marginTop: '0.25rem' }}
          >
            {loading
              ? <><span className="spinner spinner-sm" /> Classifying…</>
              : '🚀 Submit Complaint'}
          </button>
        </form>
      </div>
    </div>
  )
}
