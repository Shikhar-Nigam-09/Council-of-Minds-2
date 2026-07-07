import React from "react";

export default function CouncilLoadingState() {
  const personas = [
    { name: "Logical", color: "from-blue-500 to-indigo-600", icon: "🧠" },
    { name: "Rational", color: "from-cyan-500 to-blue-600", icon: "⚖️" },
    { name: "Practical", color: "from-emerald-500 to-teal-600", icon: "🛠️" },
    { name: "Spiritual", color: "from-purple-500 to-pink-600", icon: "✨" },
    { name: "Skeptical", color: "from-amber-500 to-orange-600", icon: "🔍" },
  ];

  return (
    <div className="flex items-start gap-4 p-6 rounded-2xl bg-white/80 dark:bg-slate-900/80 border border-indigo-500/20 shadow-lg backdrop-blur-xl animate-pulse">
      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center text-white text-lg font-bold shadow-md shadow-indigo-500/20 flex-shrink-0 animate-spin-slow">
        CM
      </div>
      <div className="space-y-4 flex-1">
        <div className="space-y-1">
          <h4 className="text-sm font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
            Council of Minds Deliberating...
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Synthesizing multi-agent evaluation across retrieved document evidence.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {personas.map((p) => (
            <div
              key={p.name}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 shadow-sm"
            >
              <span className="text-sm">{p.icon}</span>
              <span>{p.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
