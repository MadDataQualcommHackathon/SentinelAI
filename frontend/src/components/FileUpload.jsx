import { useState, useRef } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const SELECTIONS = [
  { value: 'legal_risk_scoring',    label: 'Legal Risk Scoring',     desc: 'Identifies IP, non-compete, indemnification risks' },
  { value: 'vulnerability_detection', label: 'Vulnerability Detection', desc: 'Scans code for security vulnerabilities' },
  { value: 'pii_masking',           label: 'PII Detection',           desc: 'Finds personally identifiable information' },
]

export default function FileUpload({ onResult }) {
  const [file,      setFile]      = useState(null)
  const [selection, setSelection] = useState('legal_risk_scoring')
  const [prompt,    setPrompt]    = useState('')
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [dots,      setDots]      = useState('.')
  const inputRef  = useRef(null)
  const dotsTimer = useRef(null)

  const handleFile = (e) => {
    const f = e.target.files[0]
    if (f) { setFile(f); setError(null) }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) { setFile(f); setError(null) }
  }

  const submit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    dotsTimer.current = setInterval(() =>
      setDots(d => d.length >= 3 ? '.' : d + '.'), 500)

    try {
      const form = new FormData()
      form.append('file',      file)
      form.append('selection', selection)
      form.append('prompt',    prompt)

      const res = await axios.post(`${API}/api/analyze`, form)
      onResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
    } finally {
      clearInterval(dotsTimer.current)
      setLoading(false)
      setDots('.')
    }
  }

  if (loading) {
    return (
      <div style={styles.loadingBox}>
        <div style={styles.spinner} />
        <div style={styles.loadingHeading}>
          ⚡ Analyzing on Snapdragon Hexagon NPU{dots}
        </div>
        <div style={styles.loadingFile}>{file?.name}</div>
        <div style={styles.loadingSub}>All processing happening locally. No data leaving device.</div>
      </div>
    )
  }

  return (
    <div>
      {/* Drop zone */}
      <div
        style={styles.dropzone}
        onDragOver={e => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept=".pdf" hidden onChange={handleFile} />
        <div style={styles.dropIcon}>📄</div>
        {file
          ? <div style={styles.dropFilename}>{file.name}</div>
          : <div style={styles.dropLabel}>Click or drag a PDF here</div>
        }
        <div style={styles.dropHint}>Only .pdf files are supported</div>
      </div>

      {/* Analysis type */}
      <div style={styles.section}>
        <div style={styles.label}>Analysis Type</div>
        <div style={styles.selectionGrid}>
          {SELECTIONS.map(s => (
            <button
              key={s.value}
              style={{
                ...styles.selectionBtn,
                ...(selection === s.value ? styles.selectionBtnActive : {}),
              }}
              onClick={() => setSelection(s.value)}
            >
              <div style={styles.selectionLabel}>{s.label}</div>
              <div style={styles.selectionDesc}>{s.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Prompt */}
      <div style={styles.section}>
        <div style={styles.label}>Context / Question <span style={styles.optional}>(optional)</span></div>
        <textarea
          style={styles.textarea}
          rows={3}
          placeholder="e.g. What are the biggest risks for a software contractor?"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
        />
      </div>

      {error && <div style={styles.errorBox}>{error}</div>}

      <button
        style={{ ...styles.submitBtn, ...((!file || loading) ? styles.submitBtnDisabled : {}) }}
        disabled={!file || loading}
        onClick={submit}
      >
        Analyze on NPU →
      </button>
    </div>
  )
}

const styles = {
  dropzone: {
    border: '2px dashed #334155',
    borderRadius: 12,
    padding: '48px 24px',
    textAlign: 'center',
    cursor: 'pointer',
    background: '#0f172a',
    transition: 'border-color 0.2s',
    marginBottom: 24,
  },
  dropIcon:     { fontSize: 40, marginBottom: 12 },
  dropFilename: { fontSize: 16, fontWeight: 600, color: '#60a5fa', marginBottom: 4 },
  dropLabel:    { fontSize: 16, color: '#94a3b8', marginBottom: 4 },
  dropHint:     { fontSize: 12, color: '#475569' },

  section: { marginBottom: 20 },
  label:   { fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' },
  optional: { fontWeight: 400, color: '#475569', textTransform: 'none', letterSpacing: 0 },

  selectionGrid: { display: 'flex', flexDirection: 'column', gap: 8 },
  selectionBtn: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: 10,
    padding: '12px 16px',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'border-color 0.15s, background 0.15s',
  },
  selectionBtnActive: {
    background: '#1e3a5f',
    border: '1px solid #3b82f6',
  },
  selectionLabel: { fontSize: 14, fontWeight: 600, color: '#e2e8f0', marginBottom: 2 },
  selectionDesc:  { fontSize: 12, color: '#64748b' },

  textarea: {
    width: '100%',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: 10,
    padding: '10px 14px',
    color: '#e2e8f0',
    fontSize: 14,
    resize: 'vertical',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
    outline: 'none',
  },

  errorBox: {
    background: '#450a0a',
    border: '1px solid #7f1d1d',
    borderRadius: 8,
    padding: '10px 14px',
    color: '#fca5a5',
    fontSize: 13,
    marginBottom: 16,
  },

  submitBtn: {
    display: 'block',
    width: '100%',
    padding: '14px',
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 10,
    fontSize: 15,
    fontWeight: 700,
    cursor: 'pointer',
    transition: 'background 0.15s',
  },
  submitBtnDisabled: {
    background: '#1e3a5f',
    color: '#475569',
    cursor: 'not-allowed',
  },

  loadingBox: {
    border: '1px solid #1e293b',
    borderRadius: 16,
    padding: '64px 32px',
    textAlign: 'center',
    background: '#0f172a',
  },
  spinner: {
    width: 48,
    height: 48,
    border: '4px solid #1e293b',
    borderTop: '4px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    margin: '0 auto 24px',
  },
  loadingHeading: { fontSize: 18, fontWeight: 600, color: '#60a5fa', marginBottom: 8 },
  loadingFile:    { fontSize: 13, color: '#64748b', marginBottom: 16 },
  loadingSub:     { fontSize: 12, color: '#334155' },
}
