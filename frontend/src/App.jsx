import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Sparkles,
  ShoppingBag,
  TrendingDown,
  Layers,
  Bot,
  Search,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  Zap,
  BarChart3,
  MessageSquare
} from 'lucide-react'

export default function App() {
  const [query, setQuery] = useState('')
  const [backendStatus, setBackendStatus] = useState('checking')
  const [backendInfo, setBackendInfo] = useState(null)

  useEffect(() => {
    // Check backend health status
    const checkHealth = async () => {
      try {
        const response = await axios.get('/api/health')
        if (response.data && response.data.status === 'healthy') {
          setBackendStatus('connected')
          setBackendInfo(response.data)
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        console.error('Backend health check error:', error)
        setBackendStatus('disconnected')
      }
    }

    checkHealth()
  }, [])

  const sampleQueries = [
    "Laptop under ₹60,000 for programming with 16GB RAM and good battery",
    "Best wireless ANC headphones under ₹4,000 for online meetings",
    "Smartphone under ₹25,000 with excellent camera and 5G support",
    "Lightweight student laptop under ₹45,000 with SSD and long battery life"
  ]

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShoppingBag className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                ShopWise <span className="text-indigo-400 font-extrabold">AI</span>
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                Decision Engine
              </span>
            </div>
          </div>

          {/* Backend Status Pill */}
          <div className="flex items-center space-x-2 bg-slate-900/90 px-3 py-1.5 rounded-full border border-slate-800 text-xs">
            {backendStatus === 'connected' ? (
              <>
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-slate-300 font-medium">Backend Connected</span>
                <span className="text-slate-500 text-[10px]">({backendInfo?.api_version || 'v1'})</span>
              </>
            ) : backendStatus === 'checking' ? (
              <>
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span>
                <span className="text-slate-400">Connecting to API...</span>
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-rose-400"></span>
                <span className="text-rose-300 font-medium">Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col items-center">
        <div className="text-center max-w-3xl mb-10">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            <span>RAG + Multi-Store Price Intelligence + Explainable AI</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Stop Guessing. <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Shop With Intelligence.
            </span>
          </h1>

          <p className="mt-4 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto">
            ShopWise AI searches across Amazon, Flipkart, and Croma, tracks 90-day price history, analyzes real customer reviews with RAG, and tells you whether to <span className="text-emerald-400 font-semibold">Buy Now</span> or <span className="text-amber-400 font-semibold">Wait</span>.
          </p>
        </div>

        {/* Natural Language Search Box */}
        <div className="w-full max-w-3xl bg-slate-900/90 backdrop-blur-xl p-3 rounded-2xl border border-slate-800 shadow-2xl shadow-indigo-950/30 focus-within:border-indigo-500/60 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all">
          <div className="flex items-center space-x-3 px-3 py-2">
            <Search className="h-5 w-5 text-indigo-400 shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tell AI what you need (e.g. 'Laptop under ₹60,000 for programming with 16GB RAM')..."
              className="w-full bg-transparent text-white placeholder-slate-500 focus:outline-none text-sm sm:text-base font-normal"
            />
            <button
              onClick={() => {}}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white px-5 py-2.5 rounded-xl font-medium text-sm transition-all shadow-md shadow-indigo-600/30 shrink-0 cursor-pointer"
            >
              <span>Analyze</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          {/* Quick suggestions */}
          <div className="mt-3 pt-3 border-t border-slate-800/80 px-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">
              Try searching:
            </span>
            <div className="flex flex-wrap gap-2">
              {sampleQueries.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuery(item)}
                  className="text-left text-xs bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700/50 transition-all truncate max-w-full cursor-pointer"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 4 Core Pillars Grid */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl">
          {/* Pillar 1 */}
          <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl hover:border-slate-700 transition-all group">
            <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 group-hover:scale-105 transition-transform">
              <Layers className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Cross-Store Matching</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Disambiguates titles across Amazon, Flipkart, and Croma to show unified product comparisons with direct links.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl hover:border-slate-700 transition-all group">
            <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-105 transition-transform">
              <TrendingDown className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Price Intelligence</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Analyzes 90-day moving averages and historical lows to give a definitive <span className="text-emerald-400 font-medium">Buy Now</span> or <span className="text-amber-400 font-medium">Wait</span> verdict.
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl hover:border-slate-700 transition-all group">
            <div className="h-10 w-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4 group-hover:scale-105 transition-transform">
              <MessageSquare className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Review RAG & Q&A</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Vector search across hundreds of verified reviews to extract heating, battery, and real-world performance facts.
            </p>
          </div>

          {/* Pillar 4 */}
          <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl hover:border-slate-700 transition-all group">
            <div className="h-10 w-10 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-4 group-hover:scale-105 transition-transform">
              <Bot className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Explainable AI Recs</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Transparent multi-factor scoring that tells you exactly why a product is #1 and why alternatives fell short.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>ShopWise AI — Built with FastAPI, SQLite/PostgreSQL, ChromaDB, Gemini AI & React</p>
      </footer>
    </div>
  )
}
