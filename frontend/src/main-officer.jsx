import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import AppOfficer from './AppOfficer.jsx';
import { ThemeProvider } from './contexts/ThemeContext.jsx';
import { registerServiceWorker } from './registerSW.js';

console.log('%c📄 LOADING: main-officer.jsx', 'color: #7C3AED; font-size: 12px');

// ── Register domain-aware Service Worker ─────────────────────────────
registerServiceWorker();

function AmbientBackground() {
  return (
    <div className="ambient-bg">
      <div className="ambient-orb-1" />
      <div className="ambient-orb-2" />
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <AmbientBackground />
      <AppOfficer />
    </ThemeProvider>
  </StrictMode>,
);
