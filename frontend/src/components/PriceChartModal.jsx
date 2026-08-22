import React, { useState, useEffect } from "react";
import { X, TrendingDown, TrendingUp, AlertCircle, CheckCircle, Clock } from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { getPriceAnalytics, getPriceHistory } from "../services/api";

export default function PriceChartModal({ variantId, onClose }) {
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await getPriceAnalytics(variantId);
        setAnalytics(data);

        // Format history points for Recharts
        const rawPoints = data?.history_points || [];
        const formattedHistory = rawPoints.map((item) => ({
          ...item,
          formattedDate: item.date || "N/A",
          price: item.price,
          store_name: item.store_name,
        }));
        setHistory(formattedHistory);
      } catch (err) {
        console.error("Failed to load price history", err);
      } finally {
        setLoading(false);
      }
    }
    if (variantId) {
      loadData();
    }
  }, [variantId]);

  if (!variantId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 p-2 rounded-full transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400 text-sm">Analyzing 90-day price trends with Pandas...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div>
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                90-Day Price Intelligence
              </span>
              <h2 className="text-xl font-bold text-white mt-1">
                {analytics?.product_title}
              </h2>
              <p className="text-sm text-slate-400">{analytics?.variant_name}</p>
            </div>

            {/* Verdict Banner */}
            <div
              className={`p-4 rounded-xl border flex items-start space-x-3 ${
                analytics?.verdict === "BUY_NOW"
                  ? "bg-emerald-950/40 border-emerald-500/30 text-emerald-300"
                  : analytics?.verdict === "WAIT"
                  ? "bg-amber-950/40 border-amber-500/30 text-amber-300"
                  : "bg-blue-950/40 border-blue-500/30 text-blue-300"
              }`}
            >
              {analytics?.verdict === "BUY_NOW" && (
                <CheckCircle className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
              )}
              {analytics?.verdict === "WAIT" && (
                <Clock className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              )}
              {analytics?.verdict === "FAIR_PRICE" && (
                <AlertCircle className="w-6 h-6 text-blue-400 shrink-0 mt-0.5" />
              )}
              <div>
                <div className="font-bold text-base">{analytics?.verdict_badge}</div>
                <p className="text-sm text-slate-300 mt-1">
                  {analytics?.verdict_explanation}
                </p>
              </div>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
                <div className="text-xs text-slate-400">Current Lowest</div>
                <div className="text-lg font-bold text-emerald-400 mt-0.5">
                  ₹{analytics?.current_lowest_price?.toLocaleString("en-IN")}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  on {analytics?.best_store_name}
                </div>
              </div>

              <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
                <div className="text-xs text-slate-400">30-Day Avg</div>
                <div className="text-lg font-bold text-slate-200 mt-0.5">
                  ₹{analytics?.moving_average_30d?.toLocaleString("en-IN")}
                </div>
                <div
                  className={`text-xs mt-0.5 font-medium ${
                    analytics?.price_drop_from_avg_pct < 0
                      ? "text-emerald-400"
                      : "text-amber-400"
                  }`}
                >
                  {analytics?.price_drop_from_avg_pct > 0 ? "+" : ""}
                  {analytics?.price_drop_from_avg_pct}% vs avg
                </div>
              </div>

              <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
                <div className="text-xs text-slate-400">90-Day Lowest</div>
                <div className="text-lg font-bold text-slate-200 mt-0.5">
                  ₹{analytics?.all_time_lowest_price?.toLocaleString("en-IN")}
                </div>
                <div className="text-xs text-emerald-400 mt-0.5">All-time best</div>
              </div>

              <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
                <div className="text-xs text-slate-400">90-Day Highest</div>
                <div className="text-lg font-bold text-slate-200 mt-0.5">
                  ₹{analytics?.all_time_highest_price?.toLocaleString("en-IN")}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Peak price</div>
              </div>
            </div>

            {/* Recharts Price Timeline */}
            <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-4">
              <div className="text-sm font-semibold text-slate-300 mb-3 flex items-center justify-between">
                <span>90-Day Historical Price Movement</span>
                <span className="text-xs text-slate-400">
                  Dotted Line = 30-Day Moving Avg
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={history}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                      dataKey="formattedDate"
                      stroke="#94a3b8"
                      tick={{ fontSize: 11 }}
                      minTickGap={20}
                    />
                    <YAxis
                      stroke="#94a3b8"
                      tick={{ fontSize: 11 }}
                      domain={["auto", "auto"]}
                      tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-lg text-xs">
                              <div className="text-slate-400">{data.formattedDate}</div>
                              <div className="text-emerald-400 font-bold text-sm mt-0.5">
                                ₹{data.price?.toLocaleString("en-IN")}
                              </div>
                              <div className="text-slate-300 capitalize mt-0.5">
                                Store: {data.store_name || data.store_slug}
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <ReferenceLine
                      y={analytics?.moving_average_30d}
                      stroke="#f59e0b"
                      strokeDasharray="4 4"
                      label={{
                        value: "30D Avg",
                        fill: "#f59e0b",
                        fontSize: 10,
                        position: "right",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="price"
                      stroke="#6366f1"
                      strokeWidth={2.5}
                      fillOpacity={1}
                      fill="url(#priceGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
