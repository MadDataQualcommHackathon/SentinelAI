import FileUpload from './components/FileUpload'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="inline-block px-3 py-1 text-xs bg-blue-900 text-blue-300 rounded-full mb-6 font-medium tracking-wide">
          🔒 100% On-Device — Zero Internet — Qualcomm Snapdragon X Elite
        </div>
        <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Sentinel-Edge</h1>
        <p className="text-slate-400 mb-10 text-base">
          Air-gapped AI security auditor. Upload a contract or code file.
          All analysis runs locally on the NPU.
        </p>
        <FileUpload />
      </div>
    </div>
  )
}
