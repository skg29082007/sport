import { useState } from 'react';
import { CheckCircle, Upload, Shield, XCircle, Search } from 'lucide-react';
import API from '../api';

export default function VerifyPortal() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleFileSelect(f) {
    setFile(f);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  }

  async function handleVerify() {
    if (!file) return;
    setLoading(true);
    try {
      const res = await API.verifyAsset(file);
      setResult(res);
    } catch (e) {
      setResult({ is_authentic: false, verdict: 'Verification failed: ' + e.message, confidence: 0, watermark_detected: false, similarity_score: 0, hash_distance: 999 });
    }
    setLoading(false);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Verification Portal</h1>
        <p>Upload any media to verify if it's officially registered content</p>
      </div>

      <div className="glass-card" style={{ padding: 28, maxWidth: 700 }}>
        {/* Upload */}
        <div className="upload-zone" style={{ marginBottom: 20 }}
          onClick={() => {
            const input = document.createElement('input');
            input.type = 'file'; input.accept = 'image/*';
            input.onchange = (e) => handleFileSelect(e.target.files[0]);
            input.click();
          }}
          onDrop={(e) => { e.preventDefault(); handleFileSelect(e.dataTransfer.files[0]); }}
          onDragOver={(e) => e.preventDefault()}>
          <div className="upload-icon"><Search size={36} /></div>
          <h3>Upload media to verify</h3>
          <p>We'll check it against all registered assets using AI fingerprinting</p>
        </div>

        {preview && (
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: 250, borderRadius: 12, border: '1px solid var(--border-color)' }} />
            <div style={{ marginTop: 8, fontSize: '0.82rem', color: 'var(--text-muted)' }}>{file?.name}</div>
          </div>
        )}

        <button className="btn btn-primary btn-lg w-full" onClick={handleVerify} disabled={!file || loading} style={{ justifyContent: 'center' }}>
          {loading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing...</> : <><Shield size={18} /> Verify Authenticity</>}
        </button>

        {/* Result */}
        {result && (
          <div className={`verify-result ${result.is_authentic ? 'authentic' : 'unverified'}`} style={{ marginTop: 20 }}>
            <div className="verdict-icon">{result.is_authentic ? '✅' : '⚠️'}</div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8, color: result.is_authentic ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
              {result.is_authentic ? 'VERIFIED AUTHENTIC' : 'UNVERIFIED / SUSPICIOUS'}
            </h3>
            <div className="verdict-text">{result.verdict}</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16, textAlign: 'left' }}>
              <div className="glass-card" style={{ padding: 12 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confidence</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-primary)' }}>{(result.confidence * 100).toFixed(1)}%</div>
              </div>
              <div className="glass-card" style={{ padding: 12 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Watermark</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: result.watermark_detected ? 'var(--accent-success)' : 'var(--text-muted)' }}>
                  {result.watermark_detected ? 'Found ✓' : 'Not Found'}
                </div>
              </div>
              <div className="glass-card" style={{ padding: 12 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Similarity</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{(result.similarity_score * 100).toFixed(1)}%</div>
              </div>
              <div className="glass-card" style={{ padding: 12 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Hash Distance</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{result.hash_distance.toFixed(2)}</div>
              </div>
            </div>
            {result.matched_asset_name && (
              <div style={{ marginTop: 12, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                Matched Asset: <strong>{result.matched_asset_name}</strong>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
