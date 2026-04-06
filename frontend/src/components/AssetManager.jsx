import { useState, useEffect, useCallback } from 'react';
import {
  Upload, Images, Shield, Fingerprint, Hash,
  Scan, Trash2, AlertCircle, Check
} from 'lucide-react';
import API from '../api';

export default function AssetManager() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragover, setDragover] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [scanningId, setScanningId] = useState(null);
  const [uploadMsg, setUploadMsg] = useState('');

  useEffect(() => { loadAssets(); }, []);

  async function loadAssets() {
    try {
      const data = await API.listAssets();
      setAssets(data.assets || []);
    } catch (e) { console.log('No assets yet'); }
    setLoading(false);
  }

  async function handleUpload(files) {
    if (!files.length) return;
    setUploading(true);
    setUploadMsg('');
    
    try {
      for (const file of files) {
        await API.registerAsset(file, file.name.replace(/\.[^/.]+$/, ''));
      }
      setUploadMsg(`✅ ${files.length} asset(s) registered successfully!`);
      await loadAssets();
    } catch (e) {
      setUploadMsg(`❌ Upload failed: ${e.message}`);
    }
    setUploading(false);
    setTimeout(() => setUploadMsg(''), 4000);
  }

  async function handleScan(assetId) {
    setScanningId(assetId);
    try {
      const result = await API.startScan(assetId);
      setUploadMsg(`🔍 ${result.message}`);
      await loadAssets();
    } catch (e) {
      setUploadMsg(`❌ Scan failed: ${e.message}`);
    }
    setScanningId(null);
    setTimeout(() => setUploadMsg(''), 5000);
  }

  async function handleDelete(assetId) {
    if (!confirm('Delete this asset and all associated detections?')) return;
    try {
      await API.deleteAsset(assetId);
      setSelectedAsset(null);
      await loadAssets();
    } catch (e) {
      alert('Failed to delete: ' + e.message);
    }
  }

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragover(false);
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length) handleUpload(files);
  }, []);

  const onDragOver = (e) => { e.preventDefault(); setDragover(true); };
  const onDragLeave = () => setDragover(false);

  return (
    <div>
      <div className="page-header">
        <h1>Asset Manager</h1>
        <p>Register, fingerprint, and protect your sports media assets</p>
      </div>

      {/* Upload Zone */}
      <div
        className={`upload-zone ${dragover ? 'dragover' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = 'image/*';
          input.multiple = true;
          input.onchange = (e) => handleUpload(Array.from(e.target.files));
          input.click();
        }}
        style={{ marginBottom: 20, cursor: uploading ? 'wait' : 'pointer' }}
      >
        {uploading ? (
          <>
            <div className="spinner" style={{ margin: '0 auto 12px' }} />
            <h3>Processing & Fingerprinting...</h3>
            <p>Generating perceptual hashes and embedding watermark</p>
          </>
        ) : (
          <>
            <div className="upload-icon"><Upload size={40} /></div>
            <h3>Drop media files here or click to upload</h3>
            <p>Supports JPG, PNG, WebP — Auto fingerprints with pHash + invisible watermark</p>
          </>
        )}
      </div>

      {uploadMsg && (
        <div className="glass-card" style={{
          padding: '12px 18px',
          marginBottom: 16,
          fontSize: '0.85rem',
          borderLeft: `3px solid ${uploadMsg.startsWith('✅') || uploadMsg.startsWith('🔍') ? 'var(--accent-success)' : 'var(--accent-danger)'}`,
        }}>
          {uploadMsg}
        </div>
      )}

      {/* Asset Grid */}
      <div className="section-header">
        <h2><Images size={18} style={{ marginRight: 8, verticalAlign: 'middle' }} />Protected Assets</h2>
        <span className="section-badge">{assets.length} registered</span>
      </div>

      {assets.length === 0 ? (
        <div className="glass-card empty-state">
          <div className="empty-icon"><Shield size={48} /></div>
          <h3>No assets registered</h3>
          <p>Upload sports media assets to begin digital fingerprinting and protection.</p>
        </div>
      ) : (
        <div className="asset-grid">
          {assets.map(asset => (
            <div key={asset.id} className="glass-card asset-card"
              onClick={() => setSelectedAsset(asset)}
            >
              <img
                src={`http://localhost:8000${asset.thumbnail_url}`}
                alt={asset.name}
                className="asset-image"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <div className="asset-info">
                <div className="asset-name">{asset.name}</div>
                <div className="asset-meta">
                  <span className="tag tag-green">
                    <Check size={10} /> Protected
                  </span>
                  <span className="tag tag-blue">
                    {asset.detection_count} detections
                  </span>
                  <span className="tag tag-purple">
                    <Fingerprint size={10} /> {asset.watermark_id}
                  </span>
                </div>
                <div className="hash-text" style={{ marginTop: 8 }}>
                  pHash: {asset.phash?.slice(0, 24)}...
                </div>
                <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
                  <button className="btn btn-primary btn-sm"
                    onClick={(e) => { e.stopPropagation(); handleScan(asset.id); }}
                    disabled={scanningId === asset.id}
                  >
                    {scanningId === asset.id ? (
                      <><div className="spinner" style={{ width: 12, height: 12, borderWidth: 2 }} /> Scanning...</>
                    ) : (
                      <><Scan size={12} /> Scan Web</>
                    )}
                  </button>
                  <button className="btn btn-outline btn-sm"
                    onClick={(e) => { e.stopPropagation(); handleDelete(asset.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <div className="modal-overlay" onClick={() => setSelectedAsset(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{selectedAsset.name}</h2>
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedAsset(null)}>✕</button>
            </div>
            <div style={{ display: 'grid', gap: 12 }}>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                <div style={{ marginBottom: 8 }}>
                  <strong>Status:</strong>{' '}
                  <span className="tag tag-green">{selectedAsset.status}</span>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <strong>Watermark ID:</strong>{' '}
                  <span className="hash-text">{selectedAsset.watermark_id}</span>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <strong>Detections:</strong> {selectedAsset.detection_count}
                </div>
                <div style={{ marginBottom: 8 }}>
                  <strong>Registered:</strong> {new Date(selectedAsset.created_at).toLocaleString()}
                </div>
              </div>
              <div>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 8 }}>
                  <Hash size={14} style={{ marginRight: 4 }} /> Digital Fingerprints
                </h3>
                <div className="hash-text" style={{ lineHeight: 1.8 }}>
                  <div><strong>pHash:</strong> {selectedAsset.phash}</div>
                  <div><strong>aHash:</strong> {selectedAsset.ahash}</div>
                  <div><strong>dHash:</strong> {selectedAsset.dhash}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
