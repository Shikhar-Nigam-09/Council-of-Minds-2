import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";

const AGENT_INFO = {
  logical: {
    label: "Logical Persona",
    icon: "🧠",
    desc: "Rigorous deduction, formal logic, and contradiction detection.",
    color: "from-blue-500 to-indigo-600",
  },
  rational: {
    label: "Rational Persona",
    icon: "⚖️",
    desc: "Empirical evidence synthesis, probability analysis, and tradeoffs.",
    color: "from-emerald-500 to-teal-600",
  },
  practical: {
    label: "Practical Persona",
    icon: "🛠️",
    desc: "Real-world feasibility, actionable implementation, and constraints.",
    color: "from-amber-500 to-orange-600",
  },
  spiritual: {
    label: "Spiritual Persona",
    icon: "✨",
    desc: "Ethical implications, holistic harmony, and human alignment.",
    color: "from-purple-500 to-pink-600",
  },
  skeptical: {
    label: "Skeptical Persona",
    icon: "🔬",
    desc: "Challenging assumptions, stress-testing claims, and edge cases.",
    color: "from-rose-500 to-red-600",
  },
};

const DEFAULT_WEIGHTS = {
  logical: 1.0,
  rational: 1.0,
  practical: 1.0,
  spiritual: 1.0,
  skeptical: 1.0,
};

export default function AgentWeightSlider({ initialWeights, onSave, isSaving, compact = false }) {
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (initialWeights) {
      setWeights({
        logical: Number(initialWeights.logical ?? 1.0),
        rational: Number(initialWeights.rational ?? 1.0),
        practical: Number(initialWeights.practical ?? 1.0),
        spiritual: Number(initialWeights.spiritual ?? 1.0),
        skeptical: Number(initialWeights.skeptical ?? 1.0),
      });
      setHasChanges(false);
    }
  }, [initialWeights]);

  const totalWeight = Object.values(weights).reduce((sum, val) => sum + Number(val), 0);

  const handleSliderChange = (agent, value) => {
    const numVal = parseFloat(value);
    setWeights((prev) => {
      const updated = { ...prev, [agent]: isNaN(numVal) ? 0 : numVal };
      setHasChanges(true);
      return updated;
    });
  };

  const handleRestoreDefaults = () => {
    setWeights(DEFAULT_WEIGHTS);
    setHasChanges(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (totalWeight <= 0) {
      alert("At least one agent must have a weight greater than 0.");
      return;
    }
    await onSave(weights);
    setHasChanges(false);
  };

  return (
    <Card className={`${compact ? "p-2 sm:p-4 border-0 shadow-none bg-transparent dark:bg-transparent" : "p-4 sm:p-6 md:p-8"} space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4 min-w-0">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
            <span>⚖️ Persona Synthesis Weights</span>
            <Badge variant="indigo" className="text-[10px] uppercase">
              Aggregator Config
            </Badge>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Adjust the relative influence of each reasoning persona when the Aggregator synthesizes the final answer.
          </p>
          <div className="mt-2.5 p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-900 dark:text-indigo-200 text-xs flex items-center gap-2">
            <span>💡</span>
            <span><strong>Note:</strong> Changes affect future answers only.</span>
          </div>
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleRestoreDefaults}
            disabled={isSaving}
            className="text-xs w-full sm:w-auto justify-center min-h-[36px]"
          >
            <span>🔄 Restore Defaults</span>
          </Button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4 sm:space-y-5">
          {Object.entries(AGENT_INFO).map(([key, info]) => {
            const rawVal = weights[key] ?? 1.0;
            const percentage = totalWeight > 0 ? ((rawVal / totalWeight) * 100).toFixed(1) : "0.0";

            return (
              <div
                key={key}
                className="p-3.5 sm:p-4 rounded-2xl bg-slate-50/80 dark:bg-slate-900/40 border border-slate-200/60 dark:border-slate-800/60 space-y-3 transition-all hover:border-indigo-500/30 min-w-0 break-words"
              >
                <div className="flex items-center justify-between gap-3 flex-wrap min-w-0">
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <span className="text-2xl flex-shrink-0">{info.icon}</span>
                    <div className="min-w-0">
                      <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">
                        {info.label}
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 sm:line-clamp-none">
                        {info.desc}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-right">
                      <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 block">
                        {percentage}%
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Weight: {rawVal.toFixed(1)}x
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 sm:gap-4 pt-1">
                  <span className="text-xs font-mono text-slate-400 flex-shrink-0">0.0x</span>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.1"
                    value={rawVal}
                    onChange={(e) => handleSliderChange(key, e.target.value)}
                    className="w-full h-3 sm:h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-600 dark:accent-indigo-500 focus:outline-none min-h-[28px]"
                  />
                  <span className="text-xs font-mono text-slate-400 flex-shrink-0">5.0x</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-4 gap-3">
          <div className="text-xs text-slate-500 dark:text-slate-400 font-mono text-center sm:text-left">
            Total Normalized Weight: <strong className="text-indigo-600 dark:text-indigo-400">100.0%</strong>
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={!hasChanges || isSaving || totalWeight <= 0}
            className="px-6 shadow-lg shadow-indigo-500/20 w-full sm:w-auto justify-center min-h-[40px]"
          >
            <span>{isSaving ? "Saving Weights..." : "Save Agent Weights"}</span>
          </Button>
        </div>
      </form>
    </Card>
  );
}
