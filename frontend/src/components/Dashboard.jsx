import { useState, useEffect } from 'react';
import {
  Shield, AlertTriangle, Send, Globe, Scan,
  TrendingUp, Zap, Eye
} from 'lucide-react';
import API from '../api';
import GlobalMap from './GlobalMap';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [mapPoints, setMapPoints] = useState([]);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 15000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboard() {
    try {
      const [statsData, mapData, anomalyData, detData] = await Promise.all([
        API.getDashboardStats(),
        API.getMapData(),
        API.getAnomalies(),
        API.getScanResults(null, 10),
      ]);
      setStats(statsData);
      setMapPoints(mapData.points || []);
      setAnomalies(anomalyData || []);
      setDetections(detData.detections || []);
    } catch (e) {
      console.log('Dashboard loading with defaults');
      setStats({
        assets_protected: 0,
        threats_detected: 0,
        takedowns_sent: 0,
        scan_coverage: 0,
        active_scans: 0,
        anomaly_count: 0,
      });
    }
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
      </div>
    );
  }

  const statCards = [
    {
      icon: Shield, color: 'blue', label: 'Assets Protected',
      value: stats?.assets_protected || 0,
    },
    {
      icon: AlertTriangle, color: 'red', label: 'Threats Detected',
      value: stats?.threats_detected || 0,
    },
    {
      icon: Send, color: 'purple', label: 'Takedowns Sent',
      value: stats?.takedowns_sent || 0,
    },
    {
      icon: Globe, color: 'green', label: 'Scan Coverage',
      value: `${stats?.scan_coverage || 0}%`,
    },
  ];

  function timeSince(dateStr) {
    if (!dateStr) return '';
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Command Center</h1>
        <p>Real-time digital media protection monitoring</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {statCards.map((card, i) => (
          <div key={i} className="glass-card stat-card" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className={`stat-icon ${card.color}`}>
              <card.icon size={20} />
            </div>
            <div className="stat-value">{card.value}</div>
            <div className="stat-label">{card.label}</div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        {/* Map Section */}
        <div>
          <div className="section-header">
            <h2><Globe size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />Global Detection Map</h2>
            <span className="section-badge">{mapPoints.length} active</span>
          </div>
          <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
            <GlobalMap points={mapPoints} />
          </div>

          {/* Recent Detections */}
          <div style={{ marginTop: 20 }}>
            <div className="section-header">
              <h2><Eye size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />Recent Detections</h2>
              <span className="section-badge">Live</span>
            </div>
            <div className="detection-list">
              {detections.length === 0 ? (
                <div className="glass-card empty-state">
                  <div className="empty-icon"><Scan size={48} /></div>
                  <h3>No detections yet</h3>
                  <p>Upload assets and start a scan to detect unauthorized usage across the web.</p>
                </div>
              ) : (
                detections.slice(0, 8).map((det) => (
                  <div key={det.id} className="detection-item glass-card">
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{det.asset_name}</span>
                        <span className={`tag ${
                          det.detection_type === 'exact_match' ? 'tag-red' :
                          det.detection_type === 'near_duplicate' ? 'tag-yellow' :
                          'tag-blue'
                        }`}>{det.detection_type.replace(/_/g, ' ')}</span>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {det.platform} • {det.city}, {det.country}
                      </div>
                      <div className="hash-text" style={{ marginTop: 2 }}>
                        {det.source_url}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        fontSize: '1.1rem',
                        fontWeight: 700,
                        color: det.confidence > 0.9 ? 'var(--accent-danger)' :
                               det.confidence > 0.75 ? 'var(--accent-warning)' :
                               'var(--accent-primary)',
                      }}>
                        {(det.confidence * 100).toFixed(1)}%
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                        {timeSince(det.detected_at)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Anomaly Panel */}
        <div>
          <div className="section-header">
            <h2><Zap size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />Anomaly Alerts</h2>
            <span className="section-badge" style={{
              background: anomalies.length > 0 ? 'rgba(255,61,113,0.12)' : undefined,
              color: anomalies.length > 0 ? 'var(--accent-danger)' : undefined,
            }}>
              {anomalies.length}
            </span>
          </div>

          {anomalies.length === 0 ? (
            <div className="glass-card empty-state" style={{ padding: 40 }}>
              <div className="empty-icon"><Shield size={40} /></div>
              <h3>All Clear</h3>
              <p>No anomalies detected. Start scanning to monitor content.</p>
            </div>
          ) : (
            anomalies.slice(0, 6).map((anomaly) => (
              <div key={anomaly.id} className={`anomaly-alert ${anomaly.severity}`}>
                <div className="alert-header">
                  <AlertTriangle size={14} />
                  <span className="alert-title">
                    {anomaly.anomaly_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span className={`tag tag-${
                    anomaly.severity === 'critical' ? 'red' :
                    anomaly.severity === 'high' ? 'yellow' :
                    anomaly.severity === 'medium' ? 'blue' : 'green'
                  }`}>
                    {anomaly.severity}
                  </span>
                </div>
                <div className="alert-desc">{anomaly.description}</div>
                <div className="alert-time">
                  {anomaly.asset_name} • {timeSince(anomaly.detected_at)}
                </div>
              </div>
            ))
          )}

          {/* Quick Actions */}
          <div className="glass-card" style={{ padding: 20, marginTop: 16 }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 12 }}>
              <TrendingUp size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
              Quick Actions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <button className="btn btn-primary btn-sm w-full" onClick={async () => {
                try {
                  await API.startScan();
                  loadDashboard();
                } catch (e) {
                  alert('No assets to scan. Upload assets first!');
                }
              }}>
                <Scan size={14} /> Run Full Scan
              </button>
              <a href="/assets" className="btn btn-outline btn-sm w-full" style={{ justifyContent: 'center' }}>
                <Shield size={14} /> Register Assets
              </a>
              <a href="/verify" className="btn btn-outline btn-sm w-full" style={{ justifyContent: 'center' }}>
                <Eye size={14} /> Verify Media
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
