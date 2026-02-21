const BORDER = {
  HIGH: 'border-red-700 bg-red-900/20',
  MED:  'border-orange-700 bg-orange-900/20',
  LOW:  'border-yellow-700 bg-yellow-900/20',
}
const BADGE = {
  HIGH: 'bg-red-500 text-white',
  MED:  'bg-orange-500 text-white',
  LOW:  'bg-yellow-500 text-black',
}

export default function FindingCard({ finding }) {
  const type = finding.clause_type || finding.vulnerability_type || 'Issue'
  return (
    <div className={`rounded-xl border p-5 ${BORDER[finding.risk_level] ?? 'border-slate-700'}`}>
      <div className="flex items-center gap-3 mb-3">
        <span className={`text-xs px-2 py-1 rounded font-bold ${BADGE[finding.risk_level]}`}>
          {finding.risk_level}
        </span>
        <span className="font-semibold text-white">{type}</span>
      </div>
      {finding.excerpt && (
        <code className="block text-xs text-slate-400 bg-slate-800 rounded p-3 mb-3 break-all whitespace-pre-wrap font-mono">
          {finding.excerpt}
        </code>
      )}
      <p className="text-sm text-slate-300 leading-relaxed">{finding.recommendation}</p>
    </div>
  )
}
