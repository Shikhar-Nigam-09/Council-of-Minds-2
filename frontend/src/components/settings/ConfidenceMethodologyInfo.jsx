import Card from "../ui/Card";
import Badge from "../ui/Badge";

export default function ConfidenceMethodologyInfo() {
  return (
    <Card className="p-4 sm:p-6 md:p-8 space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-4 min-w-0">
        <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
          <span>📊 Confidence Engine Methodology</span>
          <Badge variant="purple" className="text-[10px] uppercase">
            Explainable AI
          </Badge>
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Learn how Council of Minds separates subjective persona influence from objective system confidence scoring.
        </p>
      </div>

      {/* Distinction Alert */}
      <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-900 dark:text-indigo-200 text-xs space-y-2 min-w-0 break-words">
        <div className="font-bold flex items-center gap-1.5 text-sm">
          <span>⚡ Critical Distinction: User Weights vs. System Weights</span>
        </div>
        <p className="leading-relaxed opacity-90">
          <strong>User Agent Weights</strong> (configured in the tab above) control how much relative influence each reasoning persona has when the Aggregator synthesizes the final answer. They do not artificially inflate or deflate the system's confidence score.
        </p>
        <p className="leading-relaxed opacity-90">
          <strong>System Confidence Signal Weights</strong> are immutable deployment hyperparameters (configured via backend environment variables) that calculate the objective trustworthiness of an answer based on empirical grounding and consensus.
        </p>
      </div>

      {/* 3 Signals Grid */}
      <div className="space-y-4 min-w-0">
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
          The Three Confidence Signals (100% Total)
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Signal 1 */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 space-y-2 min-w-0 break-words">
            <div className="flex items-center justify-between">
              <Badge variant="blue" className="text-xs font-mono font-bold">
                Weight: 35%
              </Badge>
              <span className="text-xl">🎯</span>
            </div>
            <h5 className="text-sm font-bold text-slate-900 dark:text-white">
              Retrieval Quality
            </h5>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Measures vector relevance using L2-normalized FAISS inner products (cosine similarity) across top-k retrieved document chunks. Returns 0.0 on empty retrieval.
            </p>
          </div>

          {/* Signal 2 */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 space-y-2 min-w-0 break-words">
            <div className="flex items-center justify-between">
              <Badge variant="emerald" className="text-xs font-mono font-bold">
                Weight: 45%
              </Badge>
              <span className="text-xl">🛡️</span>
            </div>
            <h5 className="text-sm font-bold text-slate-900 dark:text-white">
              Evidence Coverage
            </h5>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              An embedding-based grounding heuristic measuring semantic evidence support across claims in the aggregated answer. Evaluates support strength rather than raw factual correctness.
            </p>
          </div>

          {/* Signal 3 */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 space-y-2 min-w-0 break-words">
            <div className="flex items-center justify-between">
              <Badge variant="purple" className="text-xs font-mono font-bold">
                Weight: 20%
              </Badge>
              <span className="text-xl">🤝</span>
            </div>
            <h5 className="text-sm font-bold text-slate-900 dark:text-white">
              Agent Agreement
            </h5>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Computes perspective convergence across successful, non-empty agent responses. Defined strictly as 0.0 if fewer than 2 successful agents respond, ensuring consensus is genuine.
            </p>
          </div>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 font-mono min-w-0 break-words overflow-wrap-anywhere">
        Formula: <strong className="text-slate-800 dark:text-slate-200">Final Score = (0.35 × Retrieval) + (0.45 × Evidence) + (0.20 × Agreement)</strong>
      </div>
    </Card>
  );
}
