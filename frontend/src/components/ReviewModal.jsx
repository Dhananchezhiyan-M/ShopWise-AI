import React, { useState, useEffect } from "react";
import { X, MessageSquare, Sparkles, Send, Star, ShieldCheck, CheckCircle2, AlertCircle } from "lucide-react";
import { getAspectSentiment, askReviewQA, getSampleReviews } from "../services/api";

export default function ReviewModal({ variantId, onClose }) {
  const [aspectData, setAspectData] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Q&A Chat state
  const [question, setQuestion] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [aspects, sampleList] = await Promise.all([
          getAspectSentiment(variantId),
          getSampleReviews(variantId),
        ]);
        setAspectData(aspects);
        setReviews(sampleList);

        // Preload default welcome Q&A
        setChatHistory([
          {
            type: "ai",
            text: `Hi! I've analyzed all verified customer reviews across Amazon, Flipkart, and Tata CLiQ for this product. Ask me anything about real-world performance, durability, or quality!`,
          },
        ]);
      } catch (err) {
        console.error("Failed to load review data", err);
      } finally {
        setLoading(false);
      }
    }
    if (variantId) {
      loadData();
    }
  }, [variantId]);

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim() || qaLoading) return;

    const userQ = question;
    setQuestion("");
    setChatHistory((prev) => [...prev, { type: "user", text: userQ }]);
    setQaLoading(true);

    try {
      const response = await askReviewQA(variantId, userQ);
      setChatHistory((prev) => [
        ...prev,
        {
          type: "ai",
          text: response.answer,
          sources: response.retrieved_sources,
        },
      ]);
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        {
          type: "ai",
          text: "I encountered an issue analyzing reviews for this question. Please try again.",
        },
      ]);
    } finally {
      setQaLoading(false);
    }
  };

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
            <p className="text-slate-400 text-sm">Querying ChromaDB vector database & aspects...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header & Overall Rating */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                  ChromaDB AI Review Intelligence
                </span>
                <h2 className="text-xl font-bold text-white mt-1">
                  {aspectData?.product_title}
                </h2>
                <div className="flex items-center space-x-2 text-xs text-slate-400 mt-1">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Based on verified multi-store customer reviews</span>
                </div>
              </div>

              <div className="bg-indigo-950/60 border border-indigo-500/30 rounded-2xl px-5 py-3 flex items-center space-x-3 shrink-0">
                <div className="text-3xl font-black text-indigo-400">
                  {aspectData?.overall_sentiment_score}
                </div>
                <div className="text-xs text-slate-300">
                  <div className="font-semibold text-white">Overall Satisfaction</div>
                  <div>Out of 10.0 ⭐</div>
                </div>
              </div>
            </div>

            {/* Aspect Satisfaction Bars */}
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center space-x-2">
                <span>Aspect Satisfaction Breakdown</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {aspectData?.aspects?.map((asp, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-3.5 space-y-2"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200 flex items-center space-x-1.5">
                        <span>{asp.icon}</span>
                        <span>{asp.label}</span>
                      </span>
                      <span className="font-bold text-emerald-400">
                        {asp.positive_percentage}% Positive
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden flex">
                      <div
                        className="bg-emerald-500 h-full"
                        style={{ width: `${asp.positive_percentage}%` }}
                      ></div>
                      <div
                        className="bg-amber-500 h-full"
                        style={{ width: `${asp.neutral_percentage}%` }}
                      ></div>
                      <div
                        className="bg-rose-500 h-full"
                        style={{ width: `${asp.negative_percentage}%` }}
                      ></div>
                    </div>

                    {/* Sample Quote */}
                    {asp.sample_positive_quote && (
                      <p className="text-[11px] text-slate-400 italic line-clamp-2">
                        "{asp.sample_positive_quote}"
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Interactive "Ask AI About This Product" Q&A Chat */}
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-4 space-y-4">
              <div className="flex items-center space-x-2 text-sm font-semibold text-indigo-300">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span>Ask AI About This Product (Grounded in Customer Reviews)</span>
              </div>

              {/* Chat Message Box */}
              <div className="space-y-3 max-h-56 overflow-y-auto pr-2">
                {chatHistory.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${
                        msg.type === "user"
                          ? "bg-indigo-600 text-white rounded-br-none"
                          : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none"
                      }`}
                    >
                      <p>{msg.text}</p>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700/50 text-[10px] text-slate-400">
                          <span className="font-semibold text-slate-300">Sources: </span>
                          {msg.sources.map((s, si) => (
                            <span key={si} className="mr-2">
                              [{s.store?.toUpperCase()} ⭐{s.rating}]
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {qaLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-800 text-slate-400 border border-slate-700 rounded-2xl p-3 text-xs flex items-center space-x-2">
                      <div className="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                      <span>Searching ChromaDB review vectors & synthesizing answer...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Q&A Input Box */}
              <form onSubmit={handleAskQuestion} className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g. Are the brakes reliable in rain? Does it tare accurately?"
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  disabled={qaLoading || !question.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Ask AI</span>
                </button>
              </form>
            </div>

            {/* Sample Verified Reviews Section */}
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-3">
                Verified Customer Reviews Drawer ({reviews.length})
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-48 overflow-y-auto pr-2">
                {reviews.map((rev) => (
                  <div
                    key={rev.id}
                    className="bg-slate-800/30 border border-slate-700/40 rounded-xl p-3 space-y-1.5 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">
                        {rev.reviewer_name}
                      </span>
                      <span className="text-[10px] bg-slate-700 px-2 py-0.5 rounded-full text-slate-300 capitalize">
                        {rev.store}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 text-amber-400 text-[11px]">
                      {"★".repeat(Math.floor(rev.rating))}
                      <span className="text-slate-400 text-[10px] ml-1">
                        {rev.rating}/5
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      "{rev.text}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
