import { useState } from 'react'
import FileUpload from './components/FileUpload'
import RiskDashboard from './components/RiskDashboard'

export default function App() {
  const [result, setResult] = useState(null)

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="mb-8">
          <span className="inline-block px-3 py-1 text-xs bg-blue-950 text-blue-400 border border-blue-800 rounded-full mb-4">
            🔒 100% On-Device &nbsp;·&nbsp; Zero Internet &nbsp;·&nbsp; Qualcomm Snapdragon X Elite
          </span>
          <h1 className="text-3xl font-bold text-white tracking-tight">Sentinel-Edge</h1>
          <p className="text-slate-400 mt-1 text-sm">
            Air-gapped AI security auditor. Upload a contract or code file — all analysis runs locally on the NPU.
          </p>
        </div>

        {result ? (
          <RiskDashboard result={result} onReset={() => setResult(null)} />
        ) : (
          <FileUpload onResult={setResult} />
        )}
      </div>
    </div>
  )
}
