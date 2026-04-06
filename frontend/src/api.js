const API_BASE = 'http://localhost:8000/api';

class SportShieldAPI {
  // ─── Assets ──────────────────────────────────────────────
  
  static async registerAsset(file, name = '') {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    
    const res = await fetch(`${API_BASE}/assets/register`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  static async listAssets() {
    const res = await fetch(`${API_BASE}/assets`);
    if (!res.ok) throw new Error('Failed to fetch assets');
    return res.json();
  }

  static async getAsset(assetId) {
    const res = await fetch(`${API_BASE}/assets/${assetId}`);
    if (!res.ok) throw new Error('Asset not found');
    return res.json();
  }

  static async verifyAsset(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_BASE}/assets/verify`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  static async deleteAsset(assetId) {
    const res = await fetch(`${API_BASE}/assets/${assetId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete asset');
    return res.json();
  }

  // ─── Scanning ────────────────────────────────────────────

  static async startScan(assetId = null) {
    const res = await fetch(`${API_BASE}/scan/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ asset_id: assetId }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  static async getScanResults(assetId = null, limit = 100) {
    const params = new URLSearchParams();
    if (assetId) params.set('asset_id', assetId);
    params.set('limit', limit);
    
    const res = await fetch(`${API_BASE}/scan/results?${params}`);
    if (!res.ok) throw new Error('Failed to fetch results');
    return res.json();
  }

  static connectLiveStream(onDetection) {
    const eventSource = new EventSource(`${API_BASE}/scan/live`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'detection') {
        onDetection(data.data);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return eventSource;
  }

  // ─── Dashboard ───────────────────────────────────────────

  static async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  }

  static async getMapData() {
    const res = await fetch(`${API_BASE}/dashboard/map`);
    if (!res.ok) throw new Error('Failed to fetch map data');
    return res.json();
  }

  static async getAnomalies() {
    const res = await fetch(`${API_BASE}/dashboard/anomalies`);
    if (!res.ok) throw new Error('Failed to fetch anomalies');
    return res.json();
  }

  static async getTimeline() {
    const res = await fetch(`${API_BASE}/dashboard/timeline`);
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return res.json();
  }

  // ─── Reports ─────────────────────────────────────────────

  static async generateDMCA(detectionId, orgName, email, notes = '') {
    const res = await fetch(`${API_BASE}/reports/dmca`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        detection_id: detectionId,
        organization_name: orgName,
        contact_email: email,
        additional_notes: notes,
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  static async listReports() {
    const res = await fetch(`${API_BASE}/reports`);
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  }
}

export default SportShieldAPI;
