import { useState, useMemo } from 'react';

// Simplified world map SVG paths for continents
const WORLD_MAP_PATHS = [
  // North America
  "M 50 80 L 55 70 L 65 65 L 80 60 L 95 55 L 105 60 L 115 70 L 120 80 L 125 90 L 135 95 L 140 100 L 135 110 L 125 115 L 115 120 L 100 125 L 90 120 L 80 110 L 70 105 L 60 95 L 50 90 Z",
  // South America
  "M 115 135 L 120 130 L 130 128 L 140 132 L 145 140 L 148 155 L 150 170 L 145 185 L 140 195 L 130 200 L 125 195 L 120 185 L 115 170 L 112 155 L 110 145 Z",
  // Europe
  "M 195 55 L 205 50 L 215 52 L 225 55 L 230 60 L 228 68 L 222 72 L 215 75 L 210 70 L 205 72 L 198 68 L 195 62 Z",
  // Africa
  "M 195 85 L 205 82 L 215 85 L 225 90 L 230 100 L 228 115 L 225 130 L 220 145 L 215 155 L 205 158 L 198 155 L 192 145 L 190 130 L 188 115 L 190 100 L 192 90 Z",
  // Asia
  "M 235 45 L 250 40 L 270 38 L 290 35 L 310 40 L 325 45 L 335 50 L 340 58 L 335 65 L 325 72 L 310 78 L 295 82 L 280 85 L 265 82 L 250 78 L 240 72 L 235 65 L 232 55 Z",
  // Australia
  "M 310 145 L 325 140 L 340 142 L 350 148 L 348 158 L 340 165 L 328 168 L 318 165 L 310 158 L 308 150 Z",
  // Greenland
  "M 110 35 L 120 30 L 130 32 L 135 38 L 130 45 L 120 48 L 112 45 Z",
];

function latLngToXY(lat, lng, width, height) {
  const x = ((lng + 180) / 360) * width;
  const latRad = (lat * Math.PI) / 180;
  const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
  const y = (height / 2) - (width * mercN) / (2 * Math.PI);
  return { x: Math.max(5, Math.min(width - 5, x)), y: Math.max(5, Math.min(height - 5, y)) };
}

function getSeverityColor(confidence) {
  if (confidence > 0.9) return '#ff3d71';
  if (confidence > 0.75) return '#ffab00';
  return '#00d4ff';
}

export default function GlobalMap({ points = [] }) {
  const [tooltip, setTooltip] = useState(null);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const width = 400;
  const height = 220;

  const mappedPoints = useMemo(() => {
    return points.map(p => ({
      ...p,
      ...latLngToXY(p.latitude, p.longitude, width, height),
    }));
  }, [points]);

  return (
    <div className="map-container" style={{ paddingTop: `${(height/width)*100}%` }}>
      <svg viewBox={`0 0 ${width} ${height}`} xmlns="http://www.w3.org/2000/svg">
        {/* Background gradient */}
        <defs>
          <radialGradient id="mapGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(0,212,255,0.03)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <rect width={width} height={height} fill="var(--bg-secondary)" />
        <rect width={width} height={height} fill="url(#mapGlow)" />

        {/* Grid lines */}
        {Array.from({ length: 9 }, (_, i) => (
          <line key={`vg${i}`} x1={(i + 1) * (width / 10)} y1={0}
            x2={(i + 1) * (width / 10)} y2={height}
            stroke="rgba(255,255,255,0.02)" strokeWidth="0.5" />
        ))}
        {Array.from({ length: 5 }, (_, i) => (
          <line key={`hg${i}`} x1={0} y1={(i + 1) * (height / 6)}
            x2={width} y2={(i + 1) * (height / 6)}
            stroke="rgba(255,255,255,0.02)" strokeWidth="0.5" />
        ))}

        {/* Continent outlines */}
        {WORLD_MAP_PATHS.map((path, i) => (
          <path key={i} d={path}
            fill="rgba(255,255,255,0.03)"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="0.5" />
        ))}

        {/* Connection lines between nearby detections */}
        {mappedPoints.slice(0, 30).map((p, i) => {
          const nearest = mappedPoints.find((q, j) => 
            j !== i && Math.hypot(q.x - p.x, q.y - p.y) < 50
          );
          if (!nearest) return null;
          return (
            <line key={`line-${i}`}
              x1={p.x} y1={p.y} x2={nearest.x} y2={nearest.y}
              stroke="rgba(0,212,255,0.08)" strokeWidth="0.3" />
          );
        })}

        {/* Detection dots */}
        {mappedPoints.map((point, i) => {
          const color = getSeverityColor(point.confidence);
          const isHovered = hoveredPoint === point.id;
          return (
            <g key={point.id}
              onMouseEnter={(e) => {
                setHoveredPoint(point.id);
                setTooltip({
                  x: e.nativeEvent.offsetX,
                  y: e.nativeEvent.offsetY,
                  data: point,
                });
              }}
              onMouseLeave={() => {
                setHoveredPoint(null);
                setTooltip(null);
              }}
              style={{ cursor: 'pointer' }}
            >
              {/* Pulse ring */}
              <circle cx={point.x} cy={point.y} r={isHovered ? 10 : 6}
                fill="none" stroke={color} strokeWidth="0.5"
                opacity={0.3}>
                <animate attributeName="r" from="3" to={isHovered ? 14 : 10}
                  dur={`${1.5 + (i % 3) * 0.5}s`} repeatCount="indefinite" />
                <animate attributeName="opacity" from="0.5" to="0"
                  dur={`${1.5 + (i % 3) * 0.5}s`} repeatCount="indefinite" />
              </circle>
              {/* Solid dot */}
              <circle cx={point.x} cy={point.y}
                r={isHovered ? 4 : 2.5}
                fill={color}
                filter="url(#glow)"
                opacity={0.9}
              />
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div style={{
          position: 'absolute',
          left: tooltip.x + 10,
          top: tooltip.y - 10,
          background: 'rgba(10,10,30,0.95)',
          border: '1px solid rgba(0,212,255,0.3)',
          borderRadius: 8,
          padding: '10px 14px',
          fontSize: '0.75rem',
          color: 'white',
          pointerEvents: 'none',
          zIndex: 10,
          minWidth: 180,
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        }}>
          <div style={{ fontWeight: 700, marginBottom: 4, color: 'var(--accent-primary)' }}>
            {tooltip.data.city}, {tooltip.data.country}
          </div>
          <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            <div>Platform: {tooltip.data.platform}</div>
            <div>Asset: {tooltip.data.asset_name}</div>
            <div>Confidence: <span style={{
              color: getSeverityColor(tooltip.data.confidence),
              fontWeight: 600,
            }}>{(tooltip.data.confidence * 100).toFixed(1)}%</span></div>
            <div>Type: {tooltip.data.detection_type?.replace(/_/g, ' ')}</div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 10,
        right: 14,
        display: 'flex',
        gap: 12,
        fontSize: '0.65rem',
        color: 'var(--text-muted)',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ff3d71' }} />
          Critical
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ffab00' }} />
          High
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#00d4ff' }} />
          Medium
        </span>
      </div>
    </div>
  );
}
