import React from "react";
import { ExternalLink, LineChart, MessageSquare, Sparkles, ShieldCheck } from "lucide-react";

export default function ProductCard({
  product,
  rank,
  compositeScore,
  badges = [],
  whyRecommended,
  onOpenPriceModal,
  onOpenReviewModal,
}) {
  const lowestPrice = product.pricing?.lowest_price || product.current_lowest_price || 0;
  const bestStore = product.pricing?.best_store_name || product.best_store_name || "Store";
  const listings = product.store_listings || [];

  return (
    <div className="bg-slate-800/90 border border-slate-700/80 hover:border-indigo-500/50 rounded-2xl p-5 flex flex-col justify-between transition-all duration-200 hover:shadow-2xl hover:shadow-indigo-500/10 group relative">
      {/* Rank / AI Score Badge if ranked */}
      {rank && (
        <div className="absolute -top-3 left-4 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white text-xs font-black px-3 py-1 rounded-full shadow-lg border border-indigo-400/40 flex items-center space-x-1 z-10">
          <Sparkles className="w-3 h-3 text-amber-300" />
          <span>#{rank} AI Top Pick</span>
          {compositeScore && <span className="opacity-90 font-normal">({compositeScore}/100)</span>}
        </div>
      )}

      <div>
        {/* Product Image & Badges */}
        <div className="relative aspect-video w-full bg-slate-900/80 rounded-xl overflow-hidden mb-4 border border-slate-700/60 mt-1">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.title}
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&auto=format&fit=crop&q=60";
              }}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-400 text-xs">
              No Image Available
            </div>
          )}
          <div className="absolute top-2 left-2 bg-slate-900/90 backdrop-blur-md border border-slate-700 px-2.5 py-0.5 rounded-md text-[11px] font-bold text-slate-200 capitalize">
            {product.category?.replace("_", " ")}
          </div>
          <div className="absolute top-2 right-2 bg-indigo-950/90 backdrop-blur-md border border-indigo-500/50 px-2.5 py-0.5 rounded-md text-[11px] font-bold text-indigo-300">
            {product.brand}
          </div>
        </div>

        {/* Title */}
        <h3 className="text-base font-bold text-white line-clamp-2 leading-snug group-hover:text-indigo-300 transition-colors">
          {product.title}
        </h3>

        {/* Specs / Variant info */}
        <p className="text-xs text-slate-400 mt-1 line-clamp-1 font-medium">
          {product.variant_name}
        </p>

        {/* AI Badges if available */}
        {badges.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2.5">
            {badges.map((b, bi) => (
              <span
                key={bi}
                className="bg-indigo-950/80 border border-indigo-500/40 text-indigo-200 text-[10px] font-semibold px-2 py-0.5 rounded"
              >
                {b}
              </span>
            ))}
          </div>
        )}

        {/* Best Price Box */}
        <div className="mt-3.5 p-3 rounded-xl bg-slate-900/80 border border-slate-700/80 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Best Live Price
            </div>
            <div className="text-xl font-black text-emerald-400 mt-0.5">
              ₹{lowestPrice.toLocaleString("en-IN")}
            </div>
          </div>
          <div className="text-right">
            <span className="inline-block bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[11px] font-bold px-2.5 py-1 rounded-md">
              Lowest on {bestStore}
            </span>
          </div>
        </div>

        {/* Store Comparison Table */}
        {listings.length > 0 && (
          <div className="mt-3.5 space-y-1.5">
            <div className="text-[11px] font-bold text-slate-400 px-1 flex justify-between uppercase tracking-wider">
              <span>Retailer Store</span>
              <span>Price</span>
            </div>
            {listings.map((listing, idx) => (
              <a
                key={idx}
                href={listing.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center justify-between p-2 rounded-lg text-xs border transition-all cursor-pointer group/store ${
                  listing.is_cheapest
                    ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-200 font-semibold hover:bg-emerald-900/50 hover:border-emerald-400"
                    : "bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700"
                }`}
                title={`Open exact listing on ${listing.store_name}`}
              >
                <div className="flex items-center space-x-2">
                  <span className="font-medium">{listing.store_name}</span>
                  {listing.is_cheapest && (
                    <span className="text-[9px] bg-emerald-500 text-slate-950 font-black px-1.5 py-0.5 rounded">
                      CHEAPEST
                    </span>
                  )}
                  {listing.rating_star && (
                    <span className="text-amber-400 text-[11px]">
                      ★ {listing.rating_star}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <span className="font-bold">
                    ₹{listing.current_price?.toLocaleString("en-IN")}
                  </span>
                  <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover/store:text-white transition-colors" />
                </div>
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 mt-5 pt-3.5 border-t border-slate-700/60">
        <button
          onClick={() => onOpenPriceModal(product.variant_id)}
          className="flex items-center justify-center space-x-1.5 bg-slate-700 hover:bg-slate-600 text-white py-2 rounded-xl text-xs font-bold transition-colors shadow-sm"
        >
          <LineChart className="w-3.5 h-3.5 text-indigo-300" />
          <span>Price Trends</span>
        </button>

        <button
          onClick={() => onOpenReviewModal(product.variant_id)}
          className="flex items-center justify-center space-x-1.5 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-xl text-xs font-bold transition-colors shadow-sm shadow-indigo-600/20"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Reviews & AI</span>
        </button>
      </div>
    </div>
  );
}

