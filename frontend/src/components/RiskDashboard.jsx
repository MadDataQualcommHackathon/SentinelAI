import FindingCard from './FindingCard'

function scoreColor(score) {
  if (score > 60) return 'text-red-400'
  if (score > 30) return 'text-orange-400'
  return 'text-green-400'
}

const PILL = {
  high:   'bg-red-900/40 text-red-400 border-red-800',
  medium: 'bg-orange-900/40 text-orange-400 border-orange-800',
  low:    'bg-yellow-900/40 text-yellow-400 border-yellow-800',
}

const RISK_ORDER = { HIGH: 0, MED: 1, LOW: 2 }

export default function RiskDashboard({ score, summary, findings }) {
  const sorted = [...findings].sort(
    (a, b) => (RISK_ORDER[a.risk_level] ?? 3) - (RISK_ORDER[b.risk_level] ?? 3)
  )

  return (
    <div>
      {/* Score + summary row */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <div>
          <div className={`text-6xl font-bold ${scoreColor(score)}`}>{score}</div>
          <div className="text-slate-500 text-sm mt-1">Risk Score (0 = safe)</div>
        </div>
        <div className="flex gap-3 flex-wrap">
          <Pill label="HIGH"   count={summary?.high ?? 0} cls={PILL.high} />
          <Pill label="MEDIUM" count={summary?.med  ?? 0} cls={PILL.medium} />
          <Pill label="LOW"    count={summary?.low  ?? 0} cls={PILL.low} />
        </div>
      </div>

      {/* Findings */}
      <div className="space-y-3">
        {sorted.length === 0 ? (
          <div className="text-center text-slate-400 py-12">
            ✅ No risks detected in this document
          </div>
        ) : (
          sorted.map((f, i) => <FindingCard key={i} finding={f} />)
        )}
      </div>
    </div>
  )
}

function Pill({ label, count, cls }) {
  return (
    <div className={`px-4 py-2 rounded-lg border text-sm font-medium ${cls}`}>
      {count} {label}
    </div>
  )
}
