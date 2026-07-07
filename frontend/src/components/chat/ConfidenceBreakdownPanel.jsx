import React from "react";

export default function ConfidenceBreakdownPanel({ breakdown }) {
  if (!breakdown) return null;

  const signals = [
    {
      name: "Retrieval Quality",
      score: breakdown.retrieval_quality_score ?? 0,
      weight: 0.35,
      desc: "FAISS vector similarity inner product across retrieved chunks.",
    },
    {
      name: "Evidence Coverage",
      score: breakdown.evidence_coverage_score ?? 0,
      weight: 0.45,
      desc: "Semantic grounding support between retrieved chunks and generated answer.",
    },
    {
      name: "Agent Agreement",
      score: breakdown.agent_agreement_score ?? 0,
      weight: 0.20,
      desc: "Perspective convergence across successful reasoning personas.",
    },
  ];

  const totalCalculated = signals.reduce(
    (sum, sig) => sum + sig.score * sig.weight,
    0
  );

  return (
    <div className="p-4 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-500/20 space-y-3 animate-fade-in">
      <h5 className="text-xs font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300 flex items-center gap-1.5">
        <span>📊</span>
        <span>Signal Score Audit Breakdown</span>
      </h5>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {signals.map((sig) => {
          const scorePercent = Math.round(sig.score * 100);
          const weightedVal = (sig.score * sig.weight * 100).toFixed(1);
          return (
            <div
              key={sig.name}
              className="p-3 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 space-y-1.5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                  {sig.name}
                </span>
                <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400">
                  {scorePercent} / 100
                </span>
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                <span>Weight: {(sig.weight * 100).toFixed(0)}%</span>
                <span>+{weightedVal} pts</span>
              </div>
              <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-tight">
                {sig.desc}
              </p>
            </div>
          );
        })}
      </div>

      <div className="pt-2 border-t border-indigo-500/10 flex items-center justify-between text-xs font-mono font-bold text-indigo-950 dark:text-indigo-200">
        <span>Weighted Sum Calculation:</span>
        <span>
          {((breakdown.final_score ?? totalCalculated) * 100).toFixed(1)} / 100
        </span>
      </div>
    </div>
  );
}
