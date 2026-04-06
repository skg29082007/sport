import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Shield,
  Images,
  Radar,
  CheckCircle,
  FileWarning,
  Activity,
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/assets', icon: Images, label: 'Assets' },
  { path: '/detections', icon: Radar, label: 'Detections' },
  { path: '/verify', icon: CheckCircle, label: 'Verify' },
  { path: '/reports', icon: FileWarning, label: 'Reports' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Shield size={24} />
        </div>
        <div className="brand-text">
          <span className="brand-name">SportShield</span>
          <span className="brand-tag">AI</span>
        </div>
      </div>

      <div className="sidebar-status">
        <Activity size={14} className="status-pulse" />
        <span>System Active</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
            {location.pathname === item.path && <div className="nav-indicator" />}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="scan-status">
          <div className="scan-dot" />
          <div className="scan-info">
            <span className="scan-label">Web Scanner</span>
            <span className="scan-value">Active — Real-time</span>
          </div>
        </div>
        <div className="version">v1.0.0 — Hackathon Build</div>
      </div>

      <style>{`
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          width: var(--sidebar-width);
          height: 100vh;
          background: rgba(8, 8, 25, 0.95);
          backdrop-filter: blur(20px);
          border-right: 1px solid var(--glass-border);
          display: flex;
          flex-direction: column;
          padding: 20px 14px;
          z-index: 100;
          overflow-y: auto;
        }

        .sidebar-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 8px 12px;
          margin-bottom: 8px;
        }

        .brand-icon {
          width: 42px;
          height: 42px;
          border-radius: 12px;
          background: var(--gradient-primary);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        }

        .brand-text {
          display: flex;
          flex-direction: column;
        }

        .brand-name {
          font-size: 1.05rem;
          font-weight: 800;
          letter-spacing: -0.02em;
          background: var(--gradient-primary);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .brand-tag {
          font-size: 0.65rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.15em;
        }

        .sidebar-status {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          margin: 4px 0 16px;
          color: var(--accent-success);
          font-size: 0.72rem;
          font-weight: 600;
          background: rgba(0, 230, 118, 0.06);
          border-radius: var(--radius-sm);
        }

        .status-pulse {
          animation: pulse-opacity 2s ease-in-out infinite;
        }

        @keyframes pulse-opacity {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        .sidebar-nav {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 11px 16px;
          border-radius: var(--radius-md);
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 0.85rem;
          font-weight: 500;
          transition: all 0.2s ease;
          position: relative;
        }

        .nav-item:hover {
          color: var(--text-primary);
          background: rgba(255, 255, 255, 0.04);
        }

        .nav-item.active {
          color: var(--accent-primary);
          background: rgba(0, 212, 255, 0.08);
          font-weight: 600;
        }

        .nav-indicator {
          position: absolute;
          right: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 20px;
          background: var(--accent-primary);
          border-radius: 3px 0 0 3px;
        }

        .sidebar-footer {
          border-top: 1px solid var(--border-color);
          padding-top: 16px;
          margin-top: 8px;
        }

        .scan-status {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          background: rgba(0, 212, 255, 0.04);
          border-radius: var(--radius-sm);
          margin-bottom: 12px;
        }

        .scan-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--accent-success);
          box-shadow: 0 0 8px var(--accent-success);
          animation: pulse-opacity 1.5s ease-in-out infinite;
        }

        .scan-info {
          display: flex;
          flex-direction: column;
        }

        .scan-label {
          font-size: 0.72rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .scan-value {
          font-size: 0.65rem;
          color: var(--text-muted);
        }

        .version {
          text-align: center;
          font-size: 0.65rem;
          color: var(--text-muted);
        }
      `}</style>
    </aside>
  );
}
