# SportShield AI

> Protecting the Integrity of Digital Sports Media

AI-powered platform for digital fingerprinting, real-time detection, and automated takedown of unauthorized sports media content.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Start Backend (Terminal 1)
```powershell
cd "build with AI"
.\venv\Scripts\activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```powershell
cd "build with AI\frontend"
npm run dev
```

Open **http://localhost:5173** in your browser.

## 📋 Demo Flow

1. **Upload Assets** → Go to Assets page, drag & drop sports images
2. **Fingerprint** → System auto-generates pHash, aHash, dHash + invisible watermark
3. **Scan Web** → Click "Scan Web" to simulate crawling for unauthorized copies
4. **View Detections** → Watch the global map light up with detection points
5. **Generate DMCA** → One-click DMCA takedown from any detection
6. **Verify Media** → Upload any image to check if it's official or stolen

## 🛡️ Technology

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| Frontend | React + Vite |
| Fingerprinting | pHash, aHash, dHash via ImageHash |
| Watermarking | DCT-domain invisible watermarking |
| Vector Search | FAISS (Meta AI) |
| Database | SQLite |
| Anomaly Detection | Statistical pattern analysis |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/assets/register | Upload & fingerprint |
| GET | /api/assets | List assets |
| POST | /api/assets/verify | Verify authenticity |
| POST | /api/scan/start | Start web scan |
| GET | /api/scan/results | Detection results |
| GET | /api/dashboard/stats | Dashboard stats |
| GET | /api/dashboard/map | Global map data |
| POST | /api/reports/dmca | Generate DMCA |

API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
SportShield AI
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic schemas
│   ├── database.py          # SQLite setup
│   ├── core/
│   │   ├── fingerprint.py   # pHash/aHash/dHash engine
│   │   ├── vector_db.py     # FAISS vector search
│   │   ├── watermark.py     # DCT watermarking
│   │   ├── crawler.py       # Web crawler simulator
│   │   ├── anomaly.py       # Anomaly detection
│   │   └── report_generator.py  # DMCA generation
│   └── routers/
│       ├── assets.py        # Asset CRUD + verify
│       ├── scan.py          # Scanning + SSE
│       ├── dashboard.py     # Stats + map
│       └── reports.py       # DMCA reports
└── frontend/
    └── src/
        ├── App.jsx           # Router
        ├── api.js            # API client
        └── components/
            ├── Dashboard.jsx     # Command center
            ├── GlobalMap.jsx     # Interactive world map
            ├── AssetManager.jsx  # Upload & manage
            ├── DetectionFeed.jsx # Detection list
            ├── VerifyPortal.jsx  # Authentication
            ├── DMCAGenerator.jsx # DMCA reports
            └── Sidebar.jsx      # Navigation
```

## 🏆 Built for Hack2Skill Challenge

**Team**: SportShield AI  
**Challenge**: Protecting the Integrity of Digital Sports Media
