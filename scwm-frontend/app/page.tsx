'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Leaf, MapPin, History, Camera, AlertTriangle } from 'lucide-react';
import dynamic from 'next/dynamic';

// --- SAFE DYNAMIC IMPORT ---
// This tells Next.js: "Do not try to render this on the server"
const MapComponent = dynamic(() => import('@/components/MapComponent'), { 
  ssr: false,
  loading: () => <div className="h-[500px] w-full bg-slate-900 animate-pulse rounded-xl flex items-center justify-center text-slate-500">Loading Map...</div>
});

// --- TYPES ---
type ScanResult = { waste_type: string; confidence: number; advice: string; scan_id?: number; };
type RecyclingCenter = { name: string; address: string; latitude: number; longitude: number; contact_info: string; };
type ScanHistory = { id: number; waste_type: string; confidence: number; timestamp: string; };

export default function Home() {
  const [activeTab, setActiveTab] = useState<'scan' | 'map' | 'history'>('scan');
  
  // State
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [centers, setCenters] = useState<RecyclingCenter[]>([]);
  const [history, setHistory] = useState<ScanHistory[]>([]);

  // Fetch Data
  useEffect(() => {
    if (activeTab === 'map') axios.get('http://localhost:8000/centers').then(res => setCenters(res.data)).catch(console.error);
    if (activeTab === 'history') axios.get('http://localhost:8000/history').then(res => setHistory(res.data)).catch(console.error);
  }, [activeTab]);

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('http://localhost:8000/analyze', formData);
      setResult(response.data);
    } catch (err) { alert("Backend Error"); } 
    finally { setLoading(false); }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500/30">
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">SCWM</h1>
          <div className="flex gap-1 bg-slate-800 p-1 rounded-lg">
            {[
              { id: 'scan', icon: Camera, label: 'Scanner' },
              { id: 'map', icon: MapPin, label: 'Map' },
              { id: 'history', icon: History, label: 'History' }
            ].map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm transition-all ${activeTab === tab.id ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}>
                <tab.icon className="w-4 h-4" /> {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto p-6">
        
        {/* --- SCANNER TAB --- */}
        {activeTab === 'scan' && (
          <div className="grid md:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-4">
            <section className="space-y-6">
              <div className="bg-slate-900 border-2 border-dashed border-slate-800 rounded-2xl p-8 text-center hover:border-emerald-500/50 transition-colors">
                {preview ? <img src={preview} className="rounded-lg shadow-2xl mx-auto max-h-64 object-cover" /> : <div className="py-12 text-slate-500"><Upload className="w-12 h-12 mx-auto mb-4 opacity-50" /><p>Upload site image</p></div>}
                <input type="file" onChange={(e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setPreview(URL.createObjectURL(e.target.files[0])); }}} className="hidden" id="upload" />
                <label htmlFor="upload" className="mt-4 inline-block bg-slate-800 px-4 py-2 rounded cursor-pointer hover:bg-slate-700 transition">Select Image</label>
              </div>
              <button onClick={handleAnalyze} disabled={!file || loading} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-emerald-900/20 disabled:opacity-50 transition-all">{loading ? "Analyzing..." : "Analyze Waste"}</button>
            </section>
            <section className="bg-slate-900 rounded-2xl p-6 border border-slate-800 h-fit">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-emerald-400"><Leaf className="w-5 h-5" /> Results</h2>
              {result ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-800 p-4 rounded-xl"><p className="text-slate-400 text-sm">Material</p><p className="text-2xl font-bold text-white">{result.waste_type}</p></div>
                    <div className="bg-slate-800 p-4 rounded-xl"><p className="text-slate-400 text-sm">Confidence</p><p className="text-2xl font-bold text-blue-400">{(result.confidence * 100).toFixed(1)}%</p></div>
                  </div>
                  <div className="bg-slate-800/50 p-5 rounded-xl border border-slate-700"><h3 className="text-slate-300 font-medium mb-2">Gemini Advice</h3><p className="text-slate-400 text-sm">{result.advice}</p></div>
                </div>
              ) : <div className="h-48 flex items-center justify-center text-slate-600 border border-dashed border-slate-800 rounded-xl">Ready to scan</div>}
            </section>
          </div>
        )}

        {/* --- MAP TAB (SAFE) --- */}
        {activeTab === 'map' && (
          <div className="animate-in fade-in">
             <div className="bg-emerald-900/20 border border-emerald-800 p-3 rounded-lg text-emerald-200 text-sm mb-4 flex gap-2 items-center">
                <AlertTriangle className="w-4 h-4" /> Showing recycling centers fetched from AWS Database
             </div>
             <MapComponent centers={centers} />
          </div>
        )}

        {/* --- HISTORY TAB --- */}
        {activeTab === 'history' && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden animate-in fade-in">
            <table className="w-full text-left">
              <thead className="bg-slate-800 text-slate-400 text-sm uppercase"><tr><th className="p-4">ID</th><th className="p-4">Type</th><th className="p-4">Confidence</th><th className="p-4">Time</th></tr></thead>
              <tbody className="divide-y divide-slate-800">
                {history.map((scan) => (
                  <tr key={scan.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="p-4 text-slate-500">#{scan.id}</td>
                    <td className="p-4 font-medium text-emerald-400">{scan.waste_type}</td>
                    <td className="p-4 text-slate-300">{(scan.confidence * 100).toFixed(0)}%</td>
                    <td className="p-4 text-slate-500 text-sm">{new Date(scan.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </main>
  );
}
