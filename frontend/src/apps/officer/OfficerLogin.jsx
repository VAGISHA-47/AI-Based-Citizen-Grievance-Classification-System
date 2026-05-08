import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Eye, EyeOff, Lock, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../../components/ui/Button';

export function OfficerLogin() {
  const navigate = useNavigate();
  const login = useAuthStore(s => s.login);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const identifier = e.target.querySelector('input[type="text"]').value;
    const passwordFields = e.target.querySelectorAll('input[type="password"], input[type="text"]');
    const password = passwordFields[1]?.value || '';
    const result = await login(identifier, password);
    setLoading(false);
    if (result.success) {
      navigate(result.jurisdiction_assigned ? '/officer' : '/officer/setup-location');
    } else {
      alert(result.error || 'Officer login failed.');
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
        {/* Brand */}
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

        {/* Form */}
        <form onSubmit={handleLogin} className="login-form">

          <div className="login-input-group">
            <label>Badge Number or Email</label>
            <div className="login-field">
              <input
                type="text"
                placeholder="BADGE-1001 or officer.id@jansetu.gov.in"
                className="login-input"
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
            {loading ? 'Authenticating…' : <><Lock size={16} /> Access Dashboard</>}
          </Button>
        </form>

        {/* Security note */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 16, fontSize: 12, color: 'var(--text-secondary)' }}>
          <Lock size={12} />
          Secure access for authorized personnel only
        </div>

        {/* Contact admin */}
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <a href="#" style={{ fontSize: 13, color: 'var(--teal-primary)', fontWeight: 500, textDecoration: 'none' }}>
            Contact administrator for access
          </a>
        </div>
      </motion.div>
    </div>
  );
}
