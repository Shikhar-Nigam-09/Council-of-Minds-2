import React from "react";

export default function EvidencePanel({ evidence = [] }) {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 italic text-center animate-fade-in">
        No document evidence chunks retrieved for this evaluation.
      </div>
    );
  }

  return (
    <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3 animate-fade-in">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
        <h5 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
          <span>📚</span>
          <span>Retrieved Document Evidence ({evidence.length} Chunks)</span>
        </h5>
        <span className="text-[10px] text-slate-400 font-mono">
          FAISS Cosine Similarity
        </span>
      </div>

      <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
        {evidence.map((chunk, index) => {
          const simPercent = chunk.similarity_score
            ? Math.round(chunk.similarity_score * 100)
            : null;

          return (
            <div
              key={index}
              className="p-3 rounded-xl bg-white dark:bg-slate-950/80 border border-slate-200/80 dark:border-slate-800/80 space-y-1.5 shadow-sm min-w-0 break-words"
            >
              <div className="flex items-center justify-between text-[11px] font-mono gap-2 min-w-0">
                <span className="font-bold text-slate-700 dark:text-slate-300 truncate pr-1">
                  {chunk.filename || `Evidence Chunk #${index + 1}`}
                </span>
                {simPercent !== null && (
                  <span className="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-bold border border-indigo-200 dark:border-indigo-800 flex-shrink-0 whitespace-nowrap">
                    {simPercent}% Match
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans line-clamp-4 hover:line-clamp-none transition-all break-words">
                "{chunk.content}"
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
