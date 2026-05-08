import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import AppCitizen from './AppCitizen.jsx';
import { ThemeProvider } from './contexts/ThemeContext.jsx';
import { registerServiceWorker } from './registerSW.js';

console.log('%c📄 LOADING: main-citizen.jsx', 'color: #00CED1; font-size: 12px');

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
      <AppCitizen />
    </ThemeProvider>
  </StrictMode>,
);
