import re

path = r"c:\Users\logit\Downloads\24hr-ku\frontend\src\app\page.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

live_card = """                  <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-lg transition-all hover:border-neutral-700">
                    <div className="p-4 border-b border-neutral-800 flex justify-between items-start bg-black/20">
                      <div>
                        <h3 className="text-sm font-bold text-white font-mono">{cam.id.split('-')[0].toUpperCase()}</h3>
                        <div className="flex items-center mt-2">
                          <div className="h-1.5 w-1.5 bg-neutral-600 rounded-full mr-2"></div>
                          <span className="text-[10px] font-bold text-neutral-500 tracking-wider uppercase">READY</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest bg-red-500/10 text-red-400 border border-red-500/20">
                          Live Source
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-black flex flex-col items-center justify-center text-neutral-600 relative border-b border-neutral-800 overflow-hidden">
                      {cam.status === 'ONLINE' && cam.stream_url ? (
                        <img src={cam.stream_url} alt={`${cam.name} stream`} className="w-full h-full object-cover" />
                      ) : (
                        <>
                          <Video className="w-10 h-10 mb-3 opacity-20" />
                          <span className="text-lg tracking-widest font-mono font-bold text-neutral-500">NO SIGNAL</span>
                          <span className="text-xs text-neutral-500 mt-2">Live stream unavailable</span>
                        </>
                      )}
                    </div>
                    <div className="p-4 flex justify-between items-center bg-black/20">
                      <div>
                        <p className="text-sm font-medium text-neutral-300">{cam.name}</p>
                        <p className="text-xs text-neutral-500 mt-0.5">{cam.location}</p>
                      </div>
                      <button 
                        onClick={() => handleRecordStream(cam.id)}
                        disabled={recording[cam.id]}
                        className="px-3 py-1.5 bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-600/30 rounded text-xs font-bold tracking-wider transition-colors disabled:opacity-50 flex items-center"
                      >
                        {recording[cam.id] ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <div className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse" />}
                        {recording[cam.id] ? "RECORDING..." : "REC 10S"}
                      </button>
                    </div>
                  </div>"""

recorded_card = """                  <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-lg transition-all hover:border-neutral-700">
                    <div className="p-4 border-b border-neutral-800 flex justify-between items-start bg-black/20">
                      <div>
                        <h3 className="text-sm font-bold text-white font-mono">{cam.id.split('-')[0].toUpperCase()}</h3>
                        <div className="flex items-center mt-2">
                          <div className="h-1.5 w-1.5 bg-neutral-600 rounded-full mr-2"></div>
                          <span className="text-[10px] font-bold text-neutral-500 tracking-wider uppercase">READY</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          Recorded Source
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-black flex flex-col items-center justify-center text-neutral-600 relative border-b border-neutral-800 overflow-hidden">
                      <Video className="w-10 h-10 mb-3 opacity-20" />
                      <span className="text-lg tracking-widest font-mono font-bold text-neutral-500">NO SIGNAL</span>
                      <span className="text-xs text-neutral-500 mt-2">Recorded footage only</span>
                    </div>
                    <div className="p-4 flex justify-between items-center bg-black/20">
                      <div>
                        <p className="text-sm font-medium text-neutral-300">{cam.name}</p>
                        <p className="text-xs text-neutral-500 mt-0.5">{cam.location}</p>
                      </div>
                    </div>
                  </div>"""

new_section = f"""        {{/* CAMERA SOURCES */}}
        <section>
          {{cameras.length > 0 ? (
            <div className="space-y-12">
              {{/* LIVE CAMERAS */}}
              {{cameras.some(c => c.source_type === 'live') && (
                <div>
                  <div className="mb-6 flex items-center">
                    <div className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse"></div>
                    <h2 className="text-xl font-bold text-white">Live Cameras</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {{cameras.filter(c => c.source_type === 'live').map(cam => (
{live_card}
                    ))}}
                  </div>
                </div>
              )}}

              {{/* RECORDED CAMERAS */}}
              {{cameras.some(c => c.source_type !== 'live') && (
                <div className="pt-8 border-t border-neutral-800">
                  <div className="mb-6">
                    <h2 className="text-xl font-bold text-white">Recorded Sources</h2>
                    <p className="text-sm text-neutral-400">Registered virtual sources and indexed footage</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {{cameras.filter(c => c.source_type !== 'live').map(cam => (
{recorded_card}
                    ))}}
                  </div>
                </div>
              )}}
            </div>
          ) : ("""

# Regex to find the whole CAMERA SOURCES section
pattern = r"\{\/\* CAMERA SOURCES \*\/\}\s*<section>.*?\{cameras\.length > 0 \? \((?:.*?)\) : \("

res = re.sub(pattern, new_section, content, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(res)
print("Updated successfully")
