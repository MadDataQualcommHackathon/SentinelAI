const SEVERITY = {
  HIGH:     { border: '#ef4444', background: 'rgba(239,68,68,0.08)',  badge: '#ef4444', text: '#fff' },
  MED:      { border: '#f97316', background: 'rgba(249,115,22,0.08)', badge: '#f97316', text: '#fff' },
  MEDIUM:   { border: '#f97316', background: 'rgba(249,115,22,0.08)', badge: '#f97316', text: '#fff' },
  LOW:      { border: '#eab308', background: 'rgba(234,179,8,0.08)',  badge: '#eab308', text: '#000' },
  CRITICAL: { border: '#dc2626', background: 'rgba(220,38,38,0.12)',  badge: '#dc2626', text: '#fff' },
  NONE:     { border: '#22c55e', background: 'rgba(34,197,94,0.08)',  badge: '#22c55e', text: '#000' },
}

function getSeverity(finding) {
  return finding.risk_level || finding.severity || 'LOW'
}

export default function FindingCard({ finding }) {
  const level   = getSeverity(finding).toUpperCase()
  const theme   = SEVERITY[level] || SEVERITY.LOW
  const title   = finding.clause_type || finding.vulnerability_type || finding.pii_type || 'Finding'
  const excerpt = finding.excerpt || finding.masked_text || ''
  const rec     = finding.recommendation || ''

  return (
    <div style={{ ...styles.card, border: `1px solid ${theme.border}`, background: theme.background }}>
      <div style={styles.header}>
        <span style={{ ...styles.badge, background: theme.badge, color: theme.text }}>
          {level}
        </span>
        <span style={styles.title}>{title}</span>
      </div>

      {excerpt && (
        <code style={styles.excerpt}>{excerpt}</code>
      )}

      {rec && (
        <p style={styles.recommendation}>{rec}</p>
      )}
    </div>
  )
}

const styles = {
  card: {
    borderRadius: 12,
    padding: '16px 20px',
    marginBottom: 12,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  badge: {
    fontSize: 11,
    fontWeight: 700,
    padding: '3px 10px',
    borderRadius: 6,
    letterSpacing: '0.06em',
    flexShrink: 0,
  },
  title: {
    fontSize: 15,
    fontWeight: 600,
    color: '#e2e8f0',
  },
  excerpt: {
    display: 'block',
    fontSize: 12,
    color: '#94a3b8',
    background: '#0f172a',
    borderRadius: 8,
    padding: '8px 12px',
    marginBottom: 10,
    wordBreak: 'break-all',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap',
  },
  recommendation: {
    fontSize: 13,
    color: '#cbd5e1',
    margin: 0,
    lineHeight: 1.5,
  },
}
