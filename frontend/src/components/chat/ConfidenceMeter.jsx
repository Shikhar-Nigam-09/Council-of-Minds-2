import React from "react";

export default function ConfidenceMeter({ score = 0, onToggleBreakdown, isBreakdownExpanded }) {
  const percentage = Math.round(score * 100);

  let badgeColor = "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  let barColor = "from-rose-500 to-red-600";
  let label = "Low";

  if (score >= 0.8) {
    badgeColor = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
    barColor = "from-emerald-500 to-teal-600";
    label = "High";
  } else if (score >= 0.5) {
    badgeColor = "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
    barColor = "from-amber-500 to-yellow-600";
    label = "Medium";
  }

  return (
    <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            System-Estimated Confidence Score
          </span>
          <span
            className={`px-2 py-0.5 rounded-md text-xs font-bold border font-mono ${badgeColor}`}
          >
            {label} ({percentage} / 100)
          </span>
        </div>

        {onToggleBreakdown && (
          <button
            onClick={onToggleBreakdown}
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 min-h-[32px] px-2 py-1 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/50 transition-colors"
          >
            <span>{isBreakdownExpanded ? "Hide Breakdown" : "View Breakdown"}</span>
            <span>{isBreakdownExpanded ? "▲" : "▼"}</span>
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${barColor} transition-all duration-500 rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
        * Reflects retrieval quality, evidence coverage, and agent agreement. Does not represent a probability of factual correctness.
      </p>
    </div>
  );
}
