import React from "react";

export default function ChallengerPanel({ challengerResponse }) {
  if (!challengerResponse) return null;

  const critiqueSummary = challengerResponse.answer || challengerResponse.critique_summary || "";
  const keyPoints = typeof challengerResponse.key_points === "object" && challengerResponse.key_points !== null
    ? challengerResponse.key_points
    : {};
  const weaknesses = Array.isArray(keyPoints.weaknesses) ? keyPoints.weaknesses : (Array.isArray(challengerResponse.weaknesses) ? challengerResponse.weaknesses : []);
  const unsupportedClaims = Array.isArray(keyPoints.unsupported_claims) ? keyPoints.unsupported_claims : (Array.isArray(challengerResponse.unsupported_claims) ? challengerResponse.unsupported_claims : []);
  const missingConsiderations = Array.isArray(keyPoints.missing_considerations) ? keyPoints.missing_considerations : (Array.isArray(challengerResponse.missing_considerations) ? challengerResponse.missing_considerations : []);

  const isSuccess = !challengerResponse.error && Boolean(
    critiqueSummary.trim() || weaknesses.length > 0 || unsupportedClaims.length > 0 || missingConsiderations.length > 0
  );
  const latency = challengerResponse.latency_ms || challengerResponse.execution_time_ms;

  return (
    <div className="p-4 sm:p-5 rounded-2xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-500/30 space-y-3 animate-fade-in shadow-sm min-w-0 break-words">
      <div className="flex items-center justify-between flex-wrap gap-2 border-b border-rose-500/10 pb-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xl flex-shrink-0">🛡️</span>
          <h4 className="text-sm font-extrabold text-rose-900 dark:text-rose-200 truncate">
            Challenger Red-Team Critique
          </h4>
          <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 whitespace-nowrap">
            Adversarial Scrutiny
          </span>
        </div>

        {latency > 0 && (
          <span className="text-xs font-mono text-rose-600/80 dark:text-rose-400/80 flex-shrink-0">
            ⏱️ {Math.round(latency)}ms
          </span>
        )}
      </div>

      {isSuccess ? (
        <div className="space-y-3">
          {critiqueSummary && (
            <div className="text-sm leading-relaxed text-rose-950 dark:text-rose-200 whitespace-pre-wrap font-sans break-words">
              {critiqueSummary}
            </div>
          )}

          {weaknesses.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-rose-500/10">
              <h5 className="text-xs font-bold text-rose-900 dark:text-rose-300">⚠️ Logical & Empirical Weaknesses:</h5>
              <ul className="list-disc list-inside text-xs space-y-1 text-rose-900/90 dark:text-rose-200/90 pl-1">
                {weaknesses.map((w, idx) => (<li key={idx} className="break-words">{w}</li>))}
              </ul>
            </div>
          )}

          {unsupportedClaims.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-rose-500/10">
              <h5 className="text-xs font-bold text-rose-900 dark:text-rose-300">🚫 Unsupported Claims:</h5>
              <ul className="list-disc list-inside text-xs space-y-1 text-rose-900/90 dark:text-rose-200/90 pl-1">
                {unsupportedClaims.map((c, idx) => (<li key={idx} className="break-words">{c}</li>))}
              </ul>
            </div>
          )}

          {missingConsiderations.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-rose-500/10">
              <h5 className="text-xs font-bold text-rose-900 dark:text-rose-300">🔍 Missing Considerations:</h5>
              <ul className="list-disc list-inside text-xs space-y-1 text-rose-900/90 dark:text-rose-200/90 pl-1">
                {missingConsiderations.map((m, idx) => (<li key={idx} className="break-words">{m}</li>))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-semibold break-words">
          ⚠️ Challenger critique unavailable:{" "}
          {challengerResponse.error || "Execution timeout or API failure"}.
        </div>
      )}
    </div>
  );
}
