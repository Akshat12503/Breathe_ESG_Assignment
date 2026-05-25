import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, FileText, Factory, Zap, Plane } from 'lucide-react';

function App() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');

  // Fetch normalized logs directly from your Django REST API
  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = () => {
    fetch('http://127.0.0.1:8000/api/activities/')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to connect to the ESG data gateway.');
        return res.json();
      })
      .then((data) => {
        setActivities(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  // Sign-off endpoint trigger
  const handleApprove = (id) => {
    fetch(`http://127.0.0.1:8000/api/activities/${id}/approve/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
      .then((res) => {
        if (res.ok) {
          fetchActivities(); // Reload state to reflect audit locks instantly
        } else {
          alert('Failed to lock data entry.');
        }
      });
  };

  // Calculate high-level sustainability KPIs for header cards
  const totalEmissions = activities
    .filter(a => a.review_status === 'APPROVED & LOCKED')
    .reduce((sum, item) => sum + parseFloat(item.co2e_emissions_mt), 0);

  const pendingCount = activities.filter(a => a.review_status === 'PENDING').length;
  const anomalyCount = activities.filter(a => a.review_status === 'SUSPICIOUS').length;

  const filteredActivities = activities.filter((activity) => {
    if (filter === 'ALL') return true;
    if (filter === 'SCOPE1') return activity.scope_category === 1;
    if (filter === 'SCOPE2') return activity.scope_category === 2;
    if (filter === 'SCOPE3') return activity.scope_category === 3;
    if (filter === 'FLAGS') return activity.review_status === 'SUSPICIOUS';
    return true;
  });

  if (loading) return <div style={styles.center}>Establishing connection to database ledger...</div>;
  if (error) return <div style={{ ...styles.center, color: '#ef4444' }}>Backend Connection Error: {error}</div>;

  return (
    <div style={styles.container}>
      {/* Header Banner */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Breathe ESG</h1>
          <p style={styles.subtitle}>Enterprise Normalization & Pre-Audit Verification Workspace</p>
        </div>
        <div style={styles.tenantBadge}>Tenant: Apex Enterprise Solutions</div>
      </header>

      {/* KPI Cards section */}
      <div style={styles.cardGrid}>
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <span style={styles.cardLabel}>Certified Ledger Balance</span>
            <ShieldCheck size={20} color="#10b981" />
          </div>
          <div style={styles.cardValue}>{totalEmissions.toFixed(2)} <span style={styles.unit}>MT CO₂e</span></div>
        </div>
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <span style={styles.cardLabel}>Pending Sign-Offs</span>
            <FileText size={20} color="#3b82f6" />
          </div>
          <div style={styles.cardValue}>{pendingCount} <span style={styles.unit}>rows awaiting review</span></div>
        </div>
        <div style={styles.card}>
          <div style={{ ...styles.card, ...styles.cardAlert }}>
            <div style={styles.cardHeader}>
              <span style={styles.cardLabel}>Flagged Anomalies</span>
              <AlertTriangle size={20} color="#f59e0b" />
            </div>
            <div style={{ ...styles.cardValue, color: '#d97706' }}>{anomalyCount} <span style={styles.unit}>suspicious rows</span></div>
          </div>
        </div>
      </div>

      {/* Filtering Bar Controls */}
      <div style={styles.filterBar}>
        {['ALL', 'SCOPE1', 'SCOPE2', 'SCOPE3', 'FLAGS'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            style={{
              ...styles.filterBtn,
              ...(filter === type ? styles.filterBtnActive : {}),
            }}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Primary Data Grid */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.theadRow}>
              <th style={styles.th}>Scope</th>
              <th style={styles.th}>Activity Detail</th>
              <th style={styles.th}>Raw Quantities</th>
              <th style={styles.th}>Unified Footprint</th>
              <th style={styles.th}>Data Lineage Source</th>
              <th style={styles.th}>Audit Status</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredActivities.map((row) => (
              <tr key={row.id} style={styles.tr}>
                <td style={styles.td}>
                  <span style={{ ...styles.scopeBadge, ...styles[`scope${row.scope_category}`] }}>
                    {row.scope_category === 1 && <Factory size={14} style={{ marginRight: 4 }} />}
                    {row.scope_category === 2 && <Zap size={14} style={{ marginRight: 4 }} />}
                    {row.scope_category === 3 && <Plane size={14} style={{ marginRight: 4 }} />}
                    Scope {row.scope_category}
                  </span>
                </td>
                <td style={styles.td}>
                  <div style={styles.boldText}>{row.activity_type}</div>
                  {row.flag_reason && <div style={styles.flagReason}>{row.flag_reason}</div>}
                </td>
                <td style={styles.td}>
                  <div style={styles.subText}>{parseFloat(row.raw_quantity).toLocaleString()} {row.raw_unit}</div>
                  {row.normalized_quantity_kwh > 0 && (
                    <div style={{ fontSize: '11px', color: '#6b7280' }}>
                      {parseFloat(row.normalized_quantity_kwh).toLocaleString()} kWh equivalent
                    </div>
                  )}
                </td>
                <td style={styles.td}>
                  <span style={styles.boldText}>{parseFloat(row.co2e_emissions_mt).toFixed(4)}</span> MT CO₂e
                </td>
                <td style={styles.td}>
                  <div style={styles.boldText}>{row.source_type}</div>
                  <div style={styles.subText}>{row.filename}</div>
                </td>
                <td style={styles.td}>
                  <span style={{ ...styles.statusBadge, ...styles[row.review_status.replace(/ & /g, '_').replace(/ /g, '_')] }}>
                    {row.review_status}
                  </span>
                </td>
                <td style={styles.td}>
                  {row.review_status !== 'APPROVED & LOCKED' ? (
                    <button onClick={() => handleApprove(row.id)} style={styles.approveBtn}>
                      Approve & Lock
                    </button>
                  ) : (
                    <CheckCircle size={20} color="#10b981" />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles = {
  container: { padding: '24px', fontFamily: 'system-ui, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', color: '#1e293b' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' },
  title: { fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#0f172a' },
  subtitle: { fontSize: '14px', color: '#64748b', margin: '4px 0 0 0' },
  tenantBadge: { backgroundColor: '#e2e8f0', padding: '6px 12px', borderRadius: '6px', fontWeight: '6px', fontSize: '13px' },
  cardGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' },
  card: { backgroundColor: '#ffffff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', color: '#64748b', fontSize: '13px', fontWeight: '500' },
  cardValue: { fontSize: '24px', fontWeight: 'bold', marginTop: '8px', color: '#0f172a' },
  unit: { fontSize: '13px', fontWeight: 'normal', color: '#64748b' },
  filterBar: { display: 'flex', gap: '8px', marginBottom: '16px' },
  filterBtn: { padding: '6px 16px', border: '1px solid #cbd5e1', borderRadius: '20px', backgroundColor: '#ffffff', cursor: 'pointer', transition: 'all 0.2s', fontSize: '13px', fontWeight: '500' },
  filterBtnActive: { backgroundColor: '#0f172a', color: '#ffffff', borderColor: '#0f172a' },
  tableWrapper: { backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
  theadRow: { backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0' },
  th: { padding: '12px 16px', fontSize: '13px', fontWeight: '600', color: '#475569' },
  tr: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '14px 16px', verticalAlign: 'top', fontSize: '14px' },
  boldText: { fontWeight: '600', color: '#0f172a' },
  subText: { color: '#64748b', fontSize: '13px' },
  flagReason: { color: '#b45309', backgroundColor: '#fef3c7', padding: '6px 10px', borderRadius: '4px', fontSize: '11px', marginTop: '6px', border: '1px solid #fde68a', maxWidth: '320px' },
  approveBtn: { backgroundColor: '#2563eb', color: '#ffffff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: '500', fontSize: '12px' },
  scopeBadge: { display: 'inline-flex', alignItems: 'center', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '600' },
  scope1: { backgroundColor: '#fee2e2', color: '#991b1b' },
  scope2: { backgroundColor: '#fef9c3', color: '#854d0e' },
  scope3: { backgroundColor: '#e0f2fe', color: '#075985' },
  statusBadge: { display: 'inline-block', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: '600' },
  PENDING: { backgroundColor: '#dbeafe', color: '#1e40af' },
  SUSPICIOUS: { backgroundColor: '#fef3c7', color: '#92400e' },
  APPROVED_LOCKED: { backgroundColor: '#d1fae5', color: '#065f46' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'sans-serif', fontSize: '16px' }
};

export default App;