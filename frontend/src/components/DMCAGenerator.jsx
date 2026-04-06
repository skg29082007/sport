import { useState, useEffect } from 'react';
import { FileWarning, FileText, Download, Clipboard } from 'lucide-react';
import API from '../api';

export default function DMCAGenerator() {
  const [detections, setDetections] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [generating, setGenerating] = useState(null);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    try {
      const [detData, repData] = await Promise.all([
        API.getScanResults(null, 50),
        API.listReports(),
      ]);
      setDetections((detData.detections || []).filter(d => d.status === 'active'));
      setReports(repData || []);
    } catch (e) { console.log('Loading...'); }
    setLoading(false);
  }

  async function handleGenerate(det) {
    setGenerating(det.id);
    try {
      const result = await API.generateDMCA(det.id);
      setSelectedReport(result);
      await loadData();
    } catch (e) { alert('Failed: ' + e.message); }
    setGenerating(null);
  }

  if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <h1>DMCA Reports</h1>
        <p>Generate and manage takedown notices for detected infringements</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Active Detections */}
        <div>
          <div className="section-header">
            <h2>Pending Takedowns</h2>
            <span className="section-badge">{detections.length}</span>
          </div>
          {detections.length === 0 ? (
            <div className="glass-card empty-state" style={{ padding: 30 }}>
              <h3>No pending detections</h3>
              <p>All detected infringements have been addressed.</p>
            </div>
          ) : (
            <div className="detection-list">
              {detections.slice(0, 15).map(det => (
                <div key={det.id} className="detection-item glass-card">
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{det.asset_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      {det.platform} • {(det.confidence * 100).toFixed(0)}% match
                    </div>
                    <div className="hash-text" style={{ marginTop: 2 }}>{det.source_url}</div>
                  </div>
                  <button className="btn btn-danger btn-sm"
                    onClick={() => handleGenerate(det)}
                    disabled={generating === det.id}>
                    {generating === det.id ? '...' : <><FileWarning size={12} /> Generate</>}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Generated Reports */}
        <div>
          <div className="section-header">
            <h2>Generated Reports</h2>
            <span className="section-badge">{reports.length}</span>
          </div>
          {reports.length === 0 ? (
            <div className="glass-card empty-state" style={{ padding: 30 }}>
              <h3>No reports yet</h3>
              <p>Generate a DMCA notice from a pending detection.</p>
            </div>
          ) : (
            <div className="detection-list">
              {reports.map(rep => (
                <div key={rep.id} className="detection-item glass-card"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setSelectedReport(rep)}>
                  <FileText size={18} style={{ color: 'var(--accent-primary)' }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                      DMCA-{rep.id.slice(0, 8).toUpperCase()}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {new Date(rep.created_at).toLocaleString()}
                    </div>
                  </div>
                  <span className="tag tag-green">Sent</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Report Modal */}
      {selectedReport && (
        <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700 }}>
                📨 DMCA-{selectedReport.id?.slice(0, 8).toUpperCase()}
              </h2>
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedReport(null)}>✕</button>
            </div>
            <div className="dmca-content">{selectedReport.content}</div>
            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <button className="btn btn-primary btn-sm" onClick={() => {
                navigator.clipboard.writeText(selectedReport.content);
                alert('Copied!');
              }}><Clipboard size={14} /> Copy</button>
              <button className="btn btn-outline btn-sm" onClick={() => {
                const blob = new Blob([selectedReport.content], { type: 'text/plain' });
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = `DMCA-${selectedReport.id?.slice(0, 8)}.txt`;
                a.click();
              }}><Download size={14} /> Download</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
