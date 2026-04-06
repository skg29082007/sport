import { useState, useEffect } from 'react';
import { Radar, ExternalLink, FileWarning, Globe, Clock } from 'lucide-react';
import API from '../api';

export default function DetectionFeed() {
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState('all');
  const [dmcaLoading, setDmcaLoading] = useState(null);
  const [dmcaResult, setDmcaResult] = useState(null);

  useEffect(() => { loadDetections(); }, []);

  async function loadDetections() {
    try {
      const data = await API.getScanResults(null, 200);
      setDetections(data.detections || []);
      setTotal(data.total || 0);
    } catch (e) { console.log('No detections'); }
    setLoading(false);
  }

  async function handleDMCA(detection) {
    setDmcaLoading(detection.id);
    try {
      const result = await API.generateDMCA(
        detection.id, 'SportShield League', 'legal@sportshield.ai'
      );
      setDmcaResult(result);
      await loadDetections();
    } catch (e) { alert('DMCA generation failed: ' + e.message); }
    setDmcaLoading(null);
  }

  function timeSince(dateStr) {
    if (!dateStr) return '';
    const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
    if (seconds < 60) return seconds + 's ago';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
    return Math.floor(seconds / 86400) + 'd ago';
  }

  const filtered = detections.filter(d => {
    if (filter === 'all') return true;
    if (filter === 'high') return d.confidence > 0.9;
    if (filter === 'active') return d.status === 'active';
    if (filter === 'dmca') return d.status === 'dmca_sent';
    return true;
  });

  if (loading) {
    return <div className="loading-spinner"><div className="spinner" /></div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Detection Feed</h1>
        <p>{total} total detections across all protected assets</p>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {['all', 'high', 'active', 'dmca'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-outline'}`}>
            {f === 'all' ? 'All' :
             f === 'high' ? '🔴 High Confidence' :
             f === 'active' ? '🟡 Active' : '📨 DMCA Sent'}
          </button>
        ))}
        <button className="btn btn-sm btn-outline"
          style={{ marginLeft: 'auto' }}
          onClick={loadDetections}>↻ Refresh</button>
      </div>

      {filtered.length === 0 ? (
        <div className="glass-card empty-state">
          <div className="empty-icon"><Radar size={48} /></div>
          <h3>No detections found</h3>
          <p>Run a scan on your registered assets to detect unauthorized usage.</p>
        </div>
      ) : (
        <div className="detection-list">
          {filtered.map(det => (
            <div key={det.id} className="detection-item glass-card">
              <div style={{ minWidth: 50, textAlign: 'center' }}>
                <div style={{
                  fontSize: '1.2rem', fontWeight: 800,
                  color: det.confidence > 0.9 ? 'var(--accent-danger)' :
                         det.confidence > 0.75 ? 'var(--accent-warning)' :
                         'var(--accent-primary)',
                }}>
                  {(det.confidence * 100).toFixed(0)}%
                </div>
                <div className="confidence-bar">
                  <div className={`confidence-fill ${
                    det.confidence > 0.9 ? 'confidence-high' :
                    det.confidence > 0.75 ? 'confidence-medium' : 'confidence-low'
                  }`} style={{ width: `${det.confidence * 100}%` }} />
                </div>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{det.asset_name}</span>
                  <span className={`tag ${
                    det.detection_type === 'exact_match' ? 'tag-red' :
                    det.detection_type === 'near_duplicate' ? 'tag-yellow' :
                    det.detection_type === 'cropped' ? 'tag-purple' : 'tag-blue'
                  }`}>{det.detection_type.replace(/_/g, ' ')}</span>
                  <span className={`tag ${det.status === 'dmca_sent' ? 'tag-green' : 'tag-yellow'}`}>
                    {det.status.replace(/_/g, ' ')}
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  <span><Globe size={12} style={{ verticalAlign: 'middle' }} /> {det.platform}</span>
                  <span>📍 {det.city}, {det.country}</span>
                  <span><Clock size={12} style={{ verticalAlign: 'middle' }} /> {timeSince(det.detected_at)}</span>
                </div>
                <div className="hash-text" style={{ marginTop: 4 }}>
                  <a href={det.source_url} target="_blank" rel="noopener noreferrer"
                    style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
                    {det.source_url} <ExternalLink size={10} />
                  </a>
                </div>
              </div>

              {det.status !== 'dmca_sent' && (
                <button className="btn btn-danger btn-sm"
                  onClick={() => handleDMCA(det)}
                  disabled={dmcaLoading === det.id}>
                  {dmcaLoading === det.id ? '...' : <><FileWarning size={12} /> DMCA</>}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {dmcaResult && (
        <div className="modal-overlay" onClick={() => setDmcaResult(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>📨 DMCA Takedown Generated</h2>
              <button className="btn btn-outline btn-sm" onClick={() => setDmcaResult(null)}>✕</button>
            </div>
            <div className="dmca-content">{dmcaResult.content}</div>
            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <button className="btn btn-primary btn-sm" onClick={() => {
                navigator.clipboard.writeText(dmcaResult.content);
                alert('Copied to clipboard!');
              }}>📋 Copy</button>
              <button className="btn btn-outline btn-sm" onClick={() => {
                const blob = new Blob([dmcaResult.content], { type: 'text/plain' });
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob); 
                a.download = `DMCA-${dmcaResult.id.slice(0, 8)}.txt`;
                a.click();
              }}>⬇ Download</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
