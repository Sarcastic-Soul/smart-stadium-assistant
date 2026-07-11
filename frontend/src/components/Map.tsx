import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

interface CrowdData {
  zone: string;
  density_pct: number;
  headcount: number;
  recommendation?: string;
}

const ZONE_POSITIONS: Record<string, { cx: number; cy: number; rx: number; ry: number }> = {
  north_stand:  { cx: 300, cy: 60,  rx: 180, ry: 35 },
  south_stand:  { cx: 300, cy: 340, rx: 180, ry: 35 },
  east_stand:   { cx: 520, cy: 200, rx: 35,  ry: 120 },
  west_stand:   { cx: 80,  cy: 200, rx: 35,  ry: 120 },
  concourse_a:  { cx: 160, cy: 130, rx: 50,  ry: 30 },
  concourse_b:  { cx: 440, cy: 270, rx: 50,  ry: 30 },
  vip_lounge:   { cx: 300, cy: 200, rx: 60,  ry: 25 },
  field_level:  { cx: 300, cy: 200, rx: 120, ry: 70 },
  parking_a:    { cx: 80,  cy: 380, rx: 50,  ry: 20 },
  parking_b:    { cx: 520, cy: 380, rx: 50,  ry: 20 },
};

function densityClass(pct: number): string {
  if (pct < 40) return 'low';
  if (pct < 65) return 'moderate';
  if (pct < 85) return 'high';
  return 'critical';
}

function zoneName(z: string): string {
  return z.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Map component — interactive SVG stadium floor plan with crowd-density heat-map.
 *
 * Fetches live crowd sensor data from the backend every 15 seconds and
 * renders colour-coded zones with occupancy percentages, headcounts,
 * and AI-generated crowd management recommendations.
 */
export default function Map() {
  const { t } = useTranslation();
  const [crowd, setCrowd] = useState<CrowdData[]>([]);
  const [hovered, setHovered] = useState<string | null>(null);

  const fetchCrowd = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/sensors/crowd');
      if (res.ok) setCrowd(await res.json());
    } catch { /* offline fallback */ }
  }, []);

  useEffect(() => {
    fetchCrowd();
    const interval = setInterval(fetchCrowd, 15000);
    return () => clearInterval(interval);
  }, [fetchCrowd]);

  const crowdMap = Object.fromEntries(crowd.map((c) => [c.zone, c]));

  return (
    <div className="map-container">
      <div className="map-viewport" role="img" aria-label={t('map.title')}>
        <svg className="stadium-svg" viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg">
          {/* Stadium outline */}
          <rect x="30" y="20" width="540" height="380" rx="80" ry="80"
            fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="2" />
          <rect x="140" y="110" width="320" height="200" rx="20"
            fill="rgba(16,185,129,0.08)" stroke="rgba(16,185,129,0.2)" strokeWidth="1" />
          {/* Field markings */}
          <line x1="300" y1="110" x2="300" y2="310" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
          <circle cx="300" cy="210" r="40" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />

          {/* Zones */}
          {Object.entries(ZONE_POSITIONS).map(([zone, pos]) => {
            const data = crowdMap[zone];
            const cls = data ? densityClass(data.density_pct) : 'low';
            return (
              <g key={zone}
                onMouseEnter={() => setHovered(zone)}
                onMouseLeave={() => setHovered(null)}
                onFocus={() => setHovered(zone)}
                onBlur={() => setHovered(null)}
                tabIndex={0}
                role="button"
                aria-label={`${zoneName(zone)}: ${data ? `${data.density_pct}%` : 'loading'}`}
              >
                <ellipse
                  className={`stadium-zone ${cls}`}
                  cx={pos.cx} cy={pos.cy} rx={pos.rx} ry={pos.ry}
                  opacity={hovered === zone ? 0.9 : 0.6}
                />
                <text className="zone-label" x={pos.cx} y={pos.cy - 6}>
                  {zoneName(zone)}
                </text>
                <text className="zone-label" x={pos.cx} y={pos.cy + 10}
                  style={{ fontSize: '10px', opacity: 0.8 }}>
                  {data ? `${data.density_pct}%` : '—'}
                </text>
              </g>
            );
          })}
        </svg>

        <div className="map-legend" aria-label="Density legend">
          {(['low', 'moderate', 'high', 'critical'] as const).map((level) => (
            <div className="legend-item" key={level}>
              <span className={`legend-dot ${level}`} aria-hidden="true" />
              <span>{t(`map.${level}`)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="map-sidebar" aria-label="Zone details">
        {crowd.map((z) => {
          const cls = densityClass(z.density_pct);
          return (
            <div className="zone-card" key={z.zone} tabIndex={0}
              aria-label={`${zoneName(z.zone)}: ${z.density_pct}% occupancy`}>
              <div className="zone-card-header">
                <span className="zone-card-name">{zoneName(z.zone)}</span>
                <span className={`zone-card-pct ${cls}`}>{z.density_pct}%</span>
              </div>
              <div className="zone-card-bar">
                <div className={`zone-card-fill ${cls}`} style={{ width: `${z.density_pct}%` }} />
              </div>
              <div className="zone-card-info">
                {t('map.headcount')}: {z.headcount.toLocaleString()}
              </div>
              {z.recommendation && (
                <div className="zone-card-rec">{z.recommendation}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
