import { useState, useEffect, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface Sustainability {
  energy_kwh: number;
  solar_generation_kwh: number;
  water_liters: number;
  waste_kg: number;
  recycling_rate_pct: number;
  carbon_offset_kg: number;
}

interface Alert {
  alert_id: string;
  severity: string;
  zone: string;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

function zoneName(z: string): string {
  return z.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Dashboard component — sustainability metrics and operational alerts.
 *
 * Displays real-time energy, water, waste, and carbon offset metrics
 * alongside severity-tagged operational alerts for venue staff.
 * Data refreshes automatically every 15 seconds.
 */
export default function Dashboard() {
  const { t } = useTranslation();
  const [metrics, setMetrics] = useState<Sustainability | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const fetchData = useCallback(async () => {
    try {
      const [sRes, aRes] = await Promise.all([
        fetch('/api/v1/sensors/sustainability'),
        fetch('/api/v1/sensors/alerts'),
      ]);
      if (sRes.ok) setMetrics(await sRes.json());
      if (aRes.ok) setAlerts(await aRes.json());
    } catch { /* offline fallback */ }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const metricCards = useMemo(() => metrics
    ? [
        { label: t('dashboard.energy'), value: metrics.energy_kwh, unit: t('dashboard.kwh'), icon: '⚡' },
        { label: t('dashboard.solar'), value: metrics.solar_generation_kwh, unit: t('dashboard.kwh'), icon: '☀️' },
        { label: t('dashboard.water'), value: metrics.water_liters, unit: t('dashboard.liters'), icon: '💧' },
        { label: t('dashboard.waste'), value: metrics.waste_kg, unit: t('dashboard.kg'), icon: '🗑️' },
        { label: t('dashboard.recycling'), value: metrics.recycling_rate_pct, unit: '%', icon: '♻️' },
        { label: t('dashboard.carbon'), value: metrics.carbon_offset_kg, unit: t('dashboard.kg'), icon: '🌱' },
      ]
    : [], [metrics, t]);

  return (
    <div className="dashboard">
      <h2 className="dashboard-title">{t('dashboard.title')}</h2>

      <section aria-labelledby="sustainability-heading">
        <h3 id="sustainability-heading" className="alerts-title">{t('dashboard.sustainability')}</h3>
        <div className="metrics-grid">
          {metricCards.map((m) => (
            <div className="metric-card" key={m.label} tabIndex={0}
              aria-label={`${m.label}: ${m.value.toLocaleString()} ${m.unit}`}>
              <div className="metric-icon" aria-hidden="true">{m.icon}</div>
              <div className="metric-label">{m.label}</div>
              <div className="metric-value">
                {m.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}
                <span className="metric-unit"> {m.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="alerts-section" aria-labelledby="alerts-heading">
        <h3 id="alerts-heading" className="alerts-title">
          🚨 {t('dashboard.alerts')} ({alerts.length})
        </h3>
        {alerts.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>{t('dashboard.noAlerts')}</p>
        ) : (
          <div className="alerts-list" role="list">
            {alerts.map((a) => (
              <div className={`alert-card ${a.severity}`} key={a.alert_id}
                role="listitem" tabIndex={0}
                aria-label={`${a.severity} alert: ${a.message}`}>
                <span className={`alert-severity ${a.severity}`}>{a.severity}</span>
                <div>
                  <div className="alert-message">{a.message}</div>
                  <div className="alert-zone">{t('map.zone')}: {zoneName(a.zone)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
