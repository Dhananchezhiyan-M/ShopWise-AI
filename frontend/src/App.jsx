import React, { useState, useEffect } from "react";
import {
  Search,
  Sparkles,
  ShoppingBag,
  RefreshCw,
  Zap,
  CheckCircle,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { getProducts, searchRecommendations } from "./services/api";
import ProductCard from "./components/ProductCard";
import PriceChartModal from "./components/PriceChartModal";
import ReviewModal from "./components/ReviewModal";

const CATEGORIES = [
  { id: "all", label: "All Categories", icon: "🛍️" },
  { id: "cycles", label: "Cycles & MTB", icon: "🚴" },
  { id: "kitchen_appliances", label: "Kitchen Scales", icon: "⚖️" },
  { id: "hardware", label: "Pipes & Hardware", icon: "🔧" },
  { id: "laptop", label: "Laptops", icon: "💻" },
  { id: "audio", label: "Audio & Headphones", icon: "🎧" },
  { id: "smartphone", label: "Smartphones", icon: "📱" },
];

const SUGGESTIONS = [
  { label: "🚴 Mountain bike under 15k", query: "I need a durable mountain bike for weekend fitness under 15000" },
  { label: "⚖️ Kitchen scale under 1k", query: "A digital kitchen scale for baking ingredients with tare function under 1000" },
  { label: "🔧 Hot water CPVC pipe", query: "Heavy duty high pressure CPVC pipe for hot water geyser line" },
  { label: "💻 16GB coding laptop under 60k", query: "Best laptop for Python coding and multitasking with 16GB RAM under 60000" },
];

export default function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [searchingAI, setSearchingAI] = useState(false);

  // Modals state
  const [activePriceModalVariant, setActivePriceModalVariant] = useState(null);
  const [activeReviewModalVariant, setActiveReviewModalVariant] = useState(null);

  // Fetch catalog when category changes
  useEffect(() => {
    setRecommendationResult(null);
    loadCatalog(selectedCategory);
  }, [selectedCategory]);

  const loadCatalog = async (category) => {
    try {
      setLoading(true);
      setError(null);
      const params = category && category !== "all" ? { category } : {};
      const data = await getProducts(params);
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch catalog", err);
      setError("Unable to connect to FastAPI backend on http://localhost:8000. Please make sure the backend server is running.");
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      handleClearSearch();
      return;
    }

    try {
      setSearchingAI(true);
      setError(null);
      const result = await searchRecommendations({
        query: searchQuery,
        category: selectedCategory !== "all" ? selectedCategory : undefined,
      });
      setRecommendationResult(result);
    } catch (err) {
      console.error("AI recommendation search failed", err);
      setError("Search request failed. Please check backend connection.");
    } finally {
      setSearchingAI(false);
    }
  };

  const handlePillClick = (query) => {
    setSearchQuery(query);
    setSearchingAI(true);
    setError(null);
    searchRecommendations({ query })
      .then((result) => setRecommendationResult(result))
      .catch((err) => {
        console.error("Search failed", err);
        setError("Search failed. Please check backend connection.");
      })
      .finally(() => setSearchingAI(false));
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setRecommendationResult(null);
    loadCatalog(selectedCategory);
  };

  // Prepare display list (either AI ranked recommendations or catalog products)
  const rankedItems = recommendationResult
    ? [
        ...(recommendationResult.top_recommendation ? [{ ...recommendationResult.top_recommendation, rank: 1 }] : []),
        ...(recommendationResult.alternative_options || []).map((item, idx) => ({ ...item, rank: idx + 2 })),
      ]
    : [];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* 1. Top Navbar */}
      <header className="sticky top-0 z-40 bg-slate-800/95 backdrop-blur-md border-b border-slate-700 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={handleClearSearch}>
            <div className="bg-gradient-to-tr from-indigo-600 to-indigo-500 p-2.5 rounded-xl text-white shadow-md shadow-indigo-600/30">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-xl tracking-tight text-white">ShopWise</span>
                <span className="bg-indigo-500/20 text-indigo-300 text-xs font-black px-2 py-0.5 rounded border border-indigo-500/40">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">
                Live Price & Review Intelligence
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 bg-slate-900/80 border border-slate-700 px-3.5 py-1.5 rounded-full shadow-inner">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Live Multi-Store AI Search</span>
          </div>
        </div>
      </header>

      {/* 2. Hero Search Section */}
      <section className="pt-8 pb-6 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full text-center">
        <div className="inline-flex items-center space-x-2 bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 text-xs font-bold px-4 py-1.5 rounded-full mb-3 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Real-Time E-Commerce Intelligence & Price Comparison</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
          Smart Product Search & <span className="bg-gradient-to-r from-indigo-400 to-indigo-200 bg-clip-text text-transparent">Live Price Tracking</span>
        </h1>
        <p className="text-sm text-slate-400 mt-2 max-w-2xl mx-auto">
          Compare prices across Amazon, Flipkart & Tata CLiQ in real-time, analyze customer reviews with AI, and track price drops.
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="mt-5 max-w-3xl mx-auto">
          <div className="relative flex items-center bg-slate-800 border-2 border-indigo-500/50 rounded-2xl shadow-xl focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-500/20 transition-all p-1.5">
            <div className="pl-3 text-indigo-400">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search any product: e.g. OnePlus Nord, Lenovo IdeaPad, Mountain Bike..."
              className="w-full bg-transparent px-3 py-2.5 text-sm text-white placeholder-slate-400 focus:outline-none font-medium"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="text-slate-400 hover:text-white p-1.5 mr-1"
                title="Clear Search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <button
              type="submit"
              disabled={searchingAI}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all shadow-md shadow-indigo-600/30 disabled:opacity-50 shrink-0"
            >
              {searchingAI ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4 text-amber-300" />
              )}
              <span>{searchingAI ? "Comparing..." : "Search Stores"}</span>
            </button>
          </div>
        </form>

        {/* Quick Suggestion Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
          <span className="text-xs font-bold text-slate-400 mr-1">Try Asking:</span>
          {SUGGESTIONS.map((pill, idx) => (
            <button
              key={idx}
              onClick={() => handlePillClick(pill.query)}
              className="bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs px-3.5 py-1.5 rounded-full transition-all font-medium shadow-sm"
            >
              {pill.label}
            </button>
          ))}
        </div>
      </section>

      {/* 3. Category Filter Tabs */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full mb-6">
        <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none border-b border-slate-800">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap flex items-center space-x-1.5 transition-all shadow-sm ${
                selectedCategory === cat.id && !recommendationResult
                  ? "bg-indigo-600 text-white shadow-indigo-600/30 scale-105"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
            </button>
          ))}
        </div>
      </section>

      {/* 4. Main Product Catalog & AI Ranked List */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex-1 w-full pb-16">
        {/* Results Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-extrabold text-white flex items-center space-x-2">
              <span>
                {recommendationResult
                  ? `AI Ranked Recommendations for "${recommendationResult.query}"`
                  : `${CATEGORIES.find((c) => c.id === selectedCategory)?.label || "Products"}`}
              </span>
              <span className="text-xs bg-slate-800 border border-slate-700 text-indigo-300 font-bold px-2.5 py-0.5 rounded-full">
                {recommendationResult
                  ? `${rankedItems.length} Ranked Picks`
                  : `${products.length} Products`}
              </span>
            </h2>
            {recommendationResult?.top_recommendation && (
              <p className="text-xs text-slate-400 mt-1 font-medium">
                Ranked by AI Multi-Factor Score (Spec Match 35% + Price Drop 25% + Review Sentiment 25% + Store Savings 15%)
              </p>
            )}
          </div>

          {recommendationResult && (
            <button
              onClick={handleClearSearch}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl transition-colors"
            >
              View Full Catalog
            </button>
          )}
        </div>

        {/* Loading Skeleton */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div
                key={n}
                className="bg-slate-800 border border-slate-700 rounded-2xl p-5 h-80 animate-pulse flex flex-col justify-between"
              >
                <div className="w-full h-40 bg-slate-700 rounded-xl"></div>
                <div className="space-y-2 mt-4">
                  <div className="h-4 bg-slate-700 rounded w-3/4"></div>
                  <div className="h-3 bg-slate-700 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-14 px-6 bg-rose-950/30 rounded-2xl border border-rose-500/40 max-w-2xl mx-auto space-y-3 shadow-xl">
            <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/40 flex items-center justify-center mx-auto text-rose-400">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Backend Connection Error</h3>
            <p className="text-xs text-rose-200 leading-relaxed font-medium">
              {error}
            </p>
            <div className="pt-2">
              <button
                onClick={() => loadCatalog(selectedCategory)}
                className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition-colors inline-flex items-center space-x-1.5 shadow-md"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry Connection</span>
              </button>
            </div>
          </div>
        ) : recommendationResult ? (
          /* Render AI Ranked Products */
          rankedItems.length === 0 ? (
            <div className="text-center py-16 bg-slate-800/60 rounded-2xl border border-slate-700">
              <ShoppingBag className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white">No matching products found</h3>
              <p className="text-xs text-slate-400 mt-1">
                Try searching with broader terms or a higher budget.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {rankedItems.map((rec) => (
                <ProductCard
                  key={rec.variant_id}
                  product={rec}
                  rank={rec.rank}
                  compositeScore={rec.composite_ai_score}
                  badges={rec.badges}
                  whyRecommended={rec.why_recommended}
                  onOpenPriceModal={(id) => setActivePriceModalVariant(id)}
                  onOpenReviewModal={(id) => setActiveReviewModalVariant(id)}
                />
              ))}
            </div>
          )
        ) : products.length === 0 ? (
          <div className="text-center py-16 bg-slate-800/60 rounded-2xl border border-slate-700">
            <ShoppingBag className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h3 className="text-base font-bold text-white">No products found in this category</h3>
            <p className="text-xs text-slate-400 mt-1">
              Click "All Categories" above to browse the entire catalog.
            </p>
          </div>
        ) : (
          /* Render Standard Catalog */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.variant_id}
                product={product}
                onOpenPriceModal={(id) => setActivePriceModalVariant(id)}
                onOpenReviewModal={(id) => setActiveReviewModalVariant(id)}
              />
            ))}
          </div>
        )}
      </main>

      {/* 5. Interactive Modals */}
      {activePriceModalVariant && (
        <PriceChartModal
          variantId={activePriceModalVariant}
          onClose={() => setActivePriceModalVariant(null)}
        />
      )}

      {activeReviewModalVariant && (
        <ReviewModal
          variantId={activeReviewModalVariant}
          onClose={() => setActiveReviewModalVariant(null)}
        />
      )}

      {/* 6. Footer */}
      <footer className="bg-slate-800 border-t border-slate-700 py-8 px-4 text-center text-xs text-slate-400 space-y-2">
        <div className="flex items-center justify-center space-x-2 font-bold text-slate-200">
          <span>ShopWise AI</span>
          <span>•</span>
          <span>FastAPI + SQLite + ChromaDB + Pandas + Gemini AI + React 19</span>
        </div>
        <p className="font-medium text-slate-400">
          Cross-Store price comparison and review intelligence across all product categories.
        </p>
      </footer>
    </div>
  );
}

