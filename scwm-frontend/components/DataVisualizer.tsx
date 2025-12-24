'use client';

export default function DataVisualizer() {
  return (
    <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-10 duration-1000">
      {/* Processing Power Card */}
      <div className="glass-panel rounded-3xl p-6 border-l-4 border-l-cyan-500">
        <div className="flex justify-between items-center mb-4">
          <span className="text-cyan-400 font-mono text-xs tracking-widest">RECOVERY_LOAD</span>
          <span className="text-cyan-400 text-xs animate-pulse">88.4%</span>
        </div>
        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-cyan-500 w-[88%] shadow-[0_0_10px_#06b6d4]"></div>
        </div>
        <p className="text-slate-500 text-[10px] mt-4 font-mono italic">Optimizing local C&D waste streams...</p>
      </div>

      {/* Sustainability Index */}
      <div className="glass-panel rounded-3xl p-6 border-l-4 border-l-emerald-500">
        <div className="flex justify-between items-center mb-4">
          <span className="text-emerald-400 font-mono text-xs tracking-widest">CO2_OFFSET</span>
          <span className="text-emerald-400 text-xs">+12.4t</span>
        </div>
        <div className="flex gap-1 h-8 items-end">
          {[40, 70, 45, 90, 65, 80, 95].map((h, i) => (
            <div 
              key={i} 
              className="flex-1 bg-emerald-500/40 rounded-t-sm animate-bounce" 
              style={{ height: `${h}%`, animationDelay: `${i * 0.1}s`, animationDuration: '3s' }}
            ></div>
          ))}
        </div>
        <p className="text-slate-500 text-[10px] mt-4 font-mono italic">Net positive impact detected.</p>
      </div>

      {/* Network Stability */}
      <div className="glass-panel rounded-3xl p-6 border-l-4 border-l-purple-500">
        <div className="flex justify-between items-center mb-4">
          <span className="text-purple-400 font-mono text-xs tracking-widest">NODE_UPTIME</span>
          <span className="text-purple-400 text-xs">99.99%</span>
        </div>
        <div className="grid grid-cols-8 gap-1">
          {[...Array(16)].map((_, i) => (
            <div key={i} className="h-2 w-2 bg-purple-500/50 rounded-full animate-ping" style={{ animationDelay: `${i * 0.2}s` }}></div>
          ))}
        </div>
        <p className="text-slate-500 text-[10px] mt-4 font-mono italic">All India nodes operational.</p>
      </div>
    </div>
  );
}