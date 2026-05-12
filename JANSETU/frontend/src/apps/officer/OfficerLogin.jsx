import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../../components/ui/Button';

export function OfficerLogin() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { loginUser } = await import('../../services/api');
      const phoneInput = e.target.querySelector('input[type="tel"]')?.value
        || e.target.querySelector('input[name="phone"]')?.value
        || e.target.querySelectorAll('input')[0]?.value;
      const passwordInput = e.target.querySelector('input[type="password"]')?.value;

      const data = await loginUser({ phone: phoneInput, password: passwordInput });

      if (data.role === 'officer' || data.role === 'admin') {
        localStorage.setItem('jansetu_token', data.access_token);
        localStorage.setItem('jansetu_role', data.role);
        localStorage.setItem('jansetu_name', data.name || 'Officer');
        localStorage.setItem('jansetu_user_id', data.user_id || '');
        navigate('/officer/dashboard');
      } else {
        setError('Access denied. Officer credentials required.');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <motion.div
        className="login-card glass glass--layer-4"
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: [-6, 0, -6], opacity: 1 }}
        transition={{
          y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
          opacity: { duration: 0.6, ease: "easeOut" }
        }}
      >
        <motion.div
          className="login-brand"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 260, damping: 22 }}
        >
          <div className="login-brand__icon">
            <Shield size={28} color="white" />
          </div>
          <h1 className="login-brand__title">JanSetu</h1>
          <p className="login-brand__subtitle">Officer Command Access</p>
        </motion.div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="login-input-group">
            <label>Mobile Number</label>
            <div className="login-field">
              <span className="login-field__prefix">
                🇮🇳 +91
                <span className="login-field__prefix-divider" />
              </span>
              <input
                type="tel"
                name="phone"
                placeholder="98765 43210"
                className="login-input has-prefix"
                required
              />
            </div>
          </div>

          <div className="login-input-group">
            <label>Password</label>
            <div className="login-field">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your secure password"
                className="login-input"
                style={{ paddingLeft: 14 }}
                required
              />
              <span className="login-input-suffix" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </span>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            loading={loading}
            style={{ marginTop: 12, height: 48, fontSize: 16 }}
          >
            {loading ? 'Authenticating…' : <><Lock size={16} style={{ marginRight: 6 }} /> Access Dashboard</>}
          </Button>

          {error && (
            <p style={{ color: '#ff6b6b', marginTop: 8, fontSize: 13, textAlign: 'center' }}>
              {error}
            </p>
          )}
        </form>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 16, fontSize: 12, color: 'var(--text-secondary)' }}>
          <Lock size={12} />
          Secure access for authorized personnel only
        </div>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <a href="#" style={{ fontSize: 13, color: 'var(--teal-primary)', fontWeight: 500, textDecoration: 'none' }}>
            Contact administrator for access
          </a>
        </div>
      </motion.div>
    </div>
  );
}
