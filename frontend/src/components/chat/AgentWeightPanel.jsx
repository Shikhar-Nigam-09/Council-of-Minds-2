import React, { useEffect } from "react";
import { useSettings } from "../../hooks/useSettings";
import AgentWeightSlider from "../settings/AgentWeightSlider";

export default function AgentWeightPanel({ isOpen, onClose }) {
  const { settings, updateAgentWeights, isUpdatingWeights } = useSettings();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-end bg-black/50 backdrop-blur-sm transition-opacity">
      {/* Backdrop */}
      <div className="fixed inset-0" onClick={onClose} />

      {/* Panel Container: Bottom sheet on mobile, right drawer on desktop */}
      <div className="relative z-10 w-full sm:w-[460px] max-h-[85vh] sm:max-h-full sm:h-full bg-white dark:bg-slate-950 border-t sm:border-t-0 sm:border-l border-slate-200 dark:border-slate-800 shadow-2xl rounded-t-3xl sm:rounded-none flex flex-col overflow-hidden animate-in sm:slide-in-from-right slide-in-from-bottom duration-300">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/80 dark:bg-slate-900/80 flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚖️</span>
            <h3 className="font-bold text-base text-slate-800 dark:text-white">
              Inline Persona Weights
            </h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-slate-200/60 dark:bg-slate-800/60 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center transition-colors font-bold text-sm"
            title="Close Panel"
            aria-label="Close Panel"
          >
            ✕
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-2 sm:p-4 overflow-y-auto flex-1">
          <AgentWeightSlider
            initialWeights={settings?.agent_weights}
            onSave={updateAgentWeights}
            isSaving={isUpdatingWeights}
            compact={true}
          />
        </div>
      </div>
    </div>
  );
}
