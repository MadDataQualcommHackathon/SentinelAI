export default function ProgressBar({ progress }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[40vh] gap-6">
      <div className="text-blue-400 text-2xl font-semibold">
        ⚡ Analyzing on Snapdragon Hexagon NPU...
      </div>
      <div className="w-full max-w-md">
        <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
          <div
            className="bg-blue-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="text-slate-400 text-sm text-center mt-3">{progress}% complete</div>
      </div>
      <p className="text-slate-600 text-xs">All processing happening locally. No data leaving device.</p>
    </div>
  )
}
