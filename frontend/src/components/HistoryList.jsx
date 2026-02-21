import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

function scoreColor(score) {
  if (score > 60) return 'bg-red-900/40 text-red-400 border-red-800'
  if (score > 30) return 'bg-orange-900/40 text-orange-400 border-orange-800'
  return 'bg-green-900/40 text-green-400 border-green-800'
}

export default function HistoryList() {
  const [history, setHistory] = useState([])

  useEffect(() => {
    axios.get(`${API}/api/history`)
      .then(r => setHistory(r.data))
      .catch(() => {})
  }, [])

  if (history.length === 0) return null

  return (
    <div className="mt-10">
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-widest mb-3">
        Past Scans
      </h2>
      <div className="space-y-2">
        {history.map(item => (
          <div
            key={item.job_id}
            className="flex items-center justify-between px-4 py-3 rounded-lg bg-slate-800 border border-slate-700"
          >
            <div className="flex items-center gap-3 min-w-0">
              <span className="text-slate-300 text-sm truncate">{item.filename}</span>
              {item.finding_count != null && (
                <span className="text-xs text-slate-500 shrink-0">{item.finding_count} findings</span>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0 ml-4">
              <span className={`text-xs px-2 py-0.5 rounded border font-medium ${scoreColor(item.score)}`}>
                {item.score}
              </span>
              <span className="text-xs text-slate-500">
                {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
