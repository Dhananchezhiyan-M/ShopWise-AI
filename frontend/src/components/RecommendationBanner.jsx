import React from "react";
import { Sparkles, Trophy, CheckCircle, ExternalLink, LineChart, MessageSquare } from "lucide-react";

export default function RecommendationBanner({
  recommendation,
  parsedCriteria,
  onOpenPriceModal,
  onOpenReviewModal,
}) {
  if (!recommendation) return null;

  return (
    <div className="bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-900 border-2 border-indigo-500/40 rounded-3xl p-6 sm:p-7 shadow-2xl relative overflow-hidden mb-8">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

      {/* Header Tag */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center space-x-2">
          <span className="bg-indigo-600 text-white p-1.5 rounded-lg">
            <Trophy className="w-4 h-4" />
          </span>
          <span className="text-sm font-bold text-indigo-300 uppercase tracking-wider">
            ShopWise AI #1 Top Pick
          </span>
        </div>

        {/* AI Score Gauge */}
        <div className="flex items-center space-x-2 bg-slate-800/80 border border-slate-700/60 px-3.5 py-1.5 rounded-full">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs font-semibold text-slate-300">Composite AI Score:</span>
          <span className="text-sm font-extrabold text-white">
            {recommendation.composite_ai_score} / 100
          </span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Product Details */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center space-x-2 text-xs text-indigo-400 font-semibold uppercase">
            <span>{recommendation.category?.replace("_", " ")}</span>
            <span>•</span>
            <span>{recommendation.brand}</span>
          </div>

          <h2 className="text-xl sm:text-2xl font-black text-white leading-tight">
            {recommendation.title}
          </h2>

          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-800/50 p-3.5 rounded-xl border border-slate-700/40">
            {recommendation.why_recommended}
          </p>

          {/* Dynamic Badges */}
          <div className="flex flex-wrap gap-2 pt-1">
            {recommendation.badges?.map((badge, idx) => (
              <span
                key={idx}
                className="bg-indigo-950/80 border border-indigo-500/30 text-indigo-200 text-xs font-medium px-3 py-1 rounded-lg"
              >
                {badge}
              </span>
            ))}
          </div>
        </div>

        {/* Price & Action Box */}
        <div className="bg-slate-800/80 border border-slate-700/70 rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="text-xs uppercase font-semibold text-slate-400">
              Best Deal Today
            </div>
            <div className="text-3xl font-black text-emerald-400 mt-1">
              ₹{recommendation.current_lowest_price?.toLocaleString("en-IN")}
            </div>
            <div className="text-xs text-slate-300 mt-1">
              Cheapest on{" "}
              <span className="font-bold text-white">{recommendation.best_store_name}</span>
            </div>
            {recommendation.savings_vs_highest_store > 0 && (
              <div className="text-xs text-emerald-400 font-semibold mt-1">
                💰 Saves ₹{recommendation.savings_vs_highest_store?.toLocaleString("en-IN")}{" "}
                vs other stores!
              </div>
            )}
          </div>

          <div className="space-y-2">
            <a
              href={recommendation.best_store_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors"
            >
              <span>Buy on {recommendation.best_store_name}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => onOpenPriceModal(recommendation.variant_id)}
                className="bg-slate-700/80 hover:bg-slate-600 text-white py-2 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1 transition-colors"
              >
                <LineChart className="w-3 h-3 text-indigo-300" />
                <span>Price Trend</span>
              </button>
              <button
                onClick={() => onOpenReviewModal(recommendation.variant_id)}
                className="bg-indigo-900/80 hover:bg-indigo-800 text-indigo-200 py-2 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1 transition-colors"
              >
                <MessageSquare className="w-3 h-3 text-indigo-300" />
                <span>Review AI</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
