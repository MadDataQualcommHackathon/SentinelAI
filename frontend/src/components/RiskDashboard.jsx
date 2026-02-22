import FindingCard from './FindingCard'

const SEVERITY_ORDER = { CRITICAL: 0, HIGH: 1, MED: 2, MEDIUM: 2, LOW: 3, NONE: 4 }

function sortBySeverity(items, key = 'risk_level') {
  return [...items].sort((a, b) => {
    const aLevel = (a[key] || a.severity || 'LOW').toUpperCase()
    const bLevel = (b[key] || b.severity || 'LOW').toUpperCase()
    return (SEVERITY_ORDER[aLevel] ?? 5) - (SEVERITY_ORDER[bLevel] ?? 5)
  })
}

function ScoreBadge({ score }) {
  const color = score > 60 ? '#ef4444' : score > 30 ? '#f97316' : '#22c55e'
  return (
    <div style={styles.scoreWrap}>
      <div style={{ ...styles.scoreNum, color }}>{score}</div>
      <div style={styles.scoreLabel}>Risk Score</div>
    </div>
  )
}

function PillCounts({ findings, piiInstances }) {
  const items = findings.length > 0 ? findings : piiInstances
  const levelKey = piiInstances.length > 0 ? 'risk_level' : 'risk_level'
  const count = (lvl) => items.filter(f => {
    const v = (f.risk_level || f.severity || '').toUpperCase()
    return v === lvl
  }).length

  return (
    <div style={styles.pills}>
      <Pill label="HIGH"   count={count('HIGH')}   color="#ef4444" bg="rgba(239,68,68,0.12)"   border="#7f1d1d" />
      <Pill label="MEDIUM" count={count('MED') + count('MEDIUM')} color="#f97316" bg="rgba(249,115,22,0.12)"  border="#7c2d12" />
      <Pill label="LOW"    count={count('LOW')}    color="#eab308" bg="rgba(234,179,8,0.12)"   border="#713f12" />
    </div>
  )
}

function Pill({ label, count, color, bg, border }) {
  return (
    <div style={{ ...styles.pill, background: bg, border: `1px solid ${border}` }}>
      <span style={{ ...styles.pillCount, color }}>{count}</span>
      <span style={styles.pillLabel}>{label}</span>
    </div>
  )
}

export default function RiskDashboard({ result, onReset }) {
  const { filename, selection, findings = [], score = 0, pii_instances = [] } = result

  const sortedFindings = sortBySeverity(findings)
  const sortedPii      = sortBySeverity(pii_instances, 'risk_level')

  const isLegal = selection === 'legal_risk_scoring'
  const isPii   = selection === 'pii_masking'
  const isVuln  = selection === 'vulnerability_detection'

  return (
    <div>
      {/* Top row */}
      <div style={styles.topRow}>
        <div>
          {isLegal && <ScoreBadge score={score} />}
          <div style={styles.filename}>{filename}</div>
          <div style={styles.selectionTag}>{selection.replace(/_/g, ' ')}</div>
        </div>
        <button style={styles.resetBtn} onClick={onReset}>
          ← Analyze Another
        </button>
      </div>

      {/* Pill counts */}
      <PillCounts findings={findings} piiInstances={pii_instances} />

      {/* Cards */}
      <div style={styles.cardList}>
        {(isLegal || isVuln) && (
          sortedFindings.length > 0
            ? sortedFindings.map((f, i) => <FindingCard key={i} finding={f} />)
            : <EmptyState />
        )}
        {isPii && (
          sortedPii.length > 0
            ? sortedPii.map((p, i) => <FindingCard key={i} finding={p} />)
            : <EmptyState />
        )}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div style={styles.empty}>✅ No issues detected</div>
  )
}

const styles = {
  topRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
    gap: 16,
  },
  scoreWrap:   { marginBottom: 6 },
  scoreNum:    { fontSize: 52, fontWeight: 800, lineHeight: 1 },
  scoreLabel:  { fontSize: 12, color: '#64748b', marginTop: 2 },
  filename:    { fontSize: 14, fontWeight: 600, color: '#e2e8f0' },
  selectionTag:{ fontSize: 12, color: '#64748b', marginTop: 2, textTransform: 'capitalize' },

  resetBtn: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: 8,
    padding: '8px 14px',
    color: '#94a3b8',
    fontSize: 13,
    cursor: 'pointer',
    flexShrink: 0,
  },

  pills: {
    display: 'flex',
    gap: 10,
    marginBottom: 24,
  },
  pill: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 14px',
    borderRadius: 8,
  },
  pillCount: { fontSize: 18, fontWeight: 700 },
  pillLabel: { fontSize: 12, color: '#94a3b8', fontWeight: 500 },

  cardList: { display: 'flex', flexDirection: 'column' },

  empty: {
    textAlign: 'center',
    color: '#475569',
    padding: '48px 0',
    fontSize: 15,
  },
}
