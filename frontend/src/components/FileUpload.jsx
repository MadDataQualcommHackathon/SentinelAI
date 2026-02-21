import { useState, useRef } from 'react'
import axios from 'axios'
import ProgressBar from './ProgressBar'
import RiskDashboard from './RiskDashboard'
import HistoryList from './HistoryList'

const API = 'http://localhost:8000'

export default function FileUpload() {
  const [file,     setFile]     = useState(null)
  const [state,    setState]    = useState('idle')  // idle | uploading | processing | complete | error
  const [progress, setProgress] = useState(0)
  const [jobId,    setJobId]    = useState(null)
  const [report,   setReport]   = useState(null)
  const timer = useRef(null)

  const start = async () => {
    if (!file) return
    setState('uploading')

    const form = new FormData()
    form.append('file', file)
    const res = await axios.post(`${API}/api/analyze`, form)
    const id  = res.data.job_id
    setJobId(id)
    setState('processing')

    timer.current = setInterval(async () => {
      const s = await axios.get(`${API}/api/status/${id}`)
      setProgress(s.data.progress || 0)

      if (s.data.status === 'complete') {
        clearInterval(timer.current)
        const r = await axios.get(`${API}/api/report/${id}`)
        setReport(r.data)
        setState('complete')
      }
      if (s.data.status === 'error') {
        clearInterval(timer.current)
        setState('error')
      }
    }, 1000)
  }

  const reset = () => {
    clearInterval(timer.current)
    setFile(null)
    setState('idle')
    setProgress(0)
    setJobId(null)
    setReport(null)
  }

  // View 2 — Processing
  if (state === 'uploading' || state === 'processing') {
    return <ProgressBar progress={progress} />
  }

  // View 3 — Results
  if (state === 'complete' && report) {
    return (
      <div>
        <div className="flex gap-3 mb-8">
          <a
            href={`${API}/api/report/${jobId}/html`}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition"
          >
            Download Report
          </a>
          <button
            onClick={reset}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition"
          >
            Analyze Another File
          </button>
        </div>
        <RiskDashboard
          score={report.score}
          summary={report.summary}
          findings={report.findings}
        />
      </div>
    )
  }

  // View 1 — Upload (idle + error)
  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition ${
          state === 'error'
            ? 'border-red-700 bg-red-900/10'
            : 'border-slate-600 hover:border-slate-500'
        }`}
      >
        <input
          type="file"
          accept=".pdf,.py,.js,.ts,.java,.sol"
          onChange={e => { setFile(e.target.files[0]); setState('idle') }}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input" className="cursor-pointer block text-slate-400 hover:text-white transition">
          <div className="text-5xl mb-4">📁</div>
          <div className="text-lg font-medium">
            {file ? file.name : 'Click to upload PDF or source code'}
          </div>
          <div className="text-sm text-slate-500 mt-2">
            Supported: .pdf .py .js .ts .java .sol
          </div>
        </label>

        {state === 'error' && (
          <p className="text-red-400 text-sm mt-4">Analysis failed. Check backend logs.</p>
        )}

        {file && (
          <button
            onClick={start}
            className="mt-6 px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition"
          >
            Analyze on NPU →
          </button>
        )}
      </div>

      <HistoryList />
    </div>
  )
}
