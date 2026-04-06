import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import AssetManager from './components/AssetManager';
import DetectionFeed from './components/DetectionFeed';
import VerifyPortal from './components/VerifyPortal';
import DMCAGenerator from './components/DMCAGenerator';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assets" element={<AssetManager />} />
            <Route path="/detections" element={<DetectionFeed />} />
            <Route path="/verify" element={<VerifyPortal />} />
            <Route path="/reports" element={<DMCAGenerator />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
