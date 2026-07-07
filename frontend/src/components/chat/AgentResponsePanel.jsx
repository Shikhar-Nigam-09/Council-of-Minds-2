import React, { useState } from "react";

const PERSONA_CONFIG = {
  logical: {
    title: "Logical Agent",
    icon: "🧠",
    badge: "Deductive & Analytical",
    bg: "bg-blue-50/50 dark:bg-blue-950/20",
    border: "border-blue-500/30",
    text: "text-blue-950 dark:text-blue-200",
    badgeBg: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  },
  rational: {
    title: "Rational Agent",
    icon: "⚖️",
    badge: "Balanced & Evidence-Based",
    bg: "bg-cyan-50/50 dark:bg-cyan-950/20",
    border: "border-cyan-500/30",
    text: "text-cyan-950 dark:text-cyan-200",
    badgeBg: "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
  },
  practical: {
    title: "Practical Agent",
    icon: "🛠️",
    badge: "Pragmatic & Actionable",
    bg: "bg-emerald-50/50 dark:bg-emerald-950/20",
    border: "border-emerald-500/30",
    text: "text-emerald-950 dark:text-emerald-200",
    badgeBg: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  },
  spiritual: {
    title: "Spiritual Agent",
    icon: "✨",
    badge: "Holistic & Meaning-Focused",
    bg: "bg-purple-50/50 dark:bg-purple-950/20",
    border: "border-purple-500/30",
    text: "text-purple-950 dark:text-purple-200",
    badgeBg: "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20",
  },
  skeptical: {
    title: "Skeptical Agent",
    icon: "🔍",
    badge: "Critical & Scrutinizing",
    bg: "bg-amber-50/50 dark:bg-amber-950/20",
    border: "border-amber-500/30",
    text: "text-amber-950 dark:text-amber-200",
    badgeBg: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  },
};

export default function AgentResponsePanel({ agentResponses = [] }) {
  const reasoningAgents = agentResponses.filter(
    (a) => a.agent_name && a.agent_name.toLowerCase() !== "challenger"
  );

  const [activeTab, setActiveTab] = useState(
    reasoningAgents[0]?.agent_name?.toLowerCase() || "logical"
  );

  if (reasoningAgents.length === 0) return null;

  const currentAgent =
    reasoningAgents.find((a) => a.agent_name?.toLowerCase() === activeTab) ||
    reasoningAgents[0];

  const config =
    PERSONA_CONFIG[currentAgent.agent_name?.toLowerCase()] || PERSONA_CONFIG.logical;

  const isSuccess = !currentAgent.error && Boolean((currentAgent.answer || currentAgent.content)?.trim());

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white/60 dark:bg-slate-900/60 shadow-sm animate-fade-in">
      {/* Tab Header */}
      <div className="flex items-center gap-1.5 p-2 sm:p-2.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 overflow-x-auto min-w-0">
        {reasoningAgents.map((agent) => {
          const nameKey = agent.agent_name?.toLowerCase();
          const conf = PERSONA_CONFIG[nameKey] || PERSONA_CONFIG.logical;
          const isSelected = activeTab === nameKey;
          const agentSuccess = !agent.error && Boolean((agent.answer || agent.content)?.trim());
          return (
            <button
              key={nameKey}
              onClick={() => setActiveTab(nameKey)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap min-h-[36px] flex-shrink-0 ${
                isSelected
                  ? `${conf.bg} ${conf.text} border ${conf.border} shadow-sm`
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-slate-800/60"
              }`}
            >
              <span>{conf.icon}</span>
              <span className="capitalize">{agent.agent_name}</span>
              {!agentSuccess && (
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block ml-1" title="Unavailable" />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className={`p-4 sm:p-5 ${config.bg} space-y-4 min-w-0 break-words`}>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xl">{config.icon}</span>
            <h4 className={`text-sm font-extrabold ${config.text}`}>
              {config.title}
            </h4>
            <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold border ${config.badgeBg}`}>
              {config.badge}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-slate-500 dark:text-slate-400">
            {currentAgent.self_reported_confidence !== null &&
              currentAgent.self_reported_confidence !== undefined && (
                <span>
                  Self-Reported Confidence:{" "}
                  <strong className={config.text}>
                    {Math.round(currentAgent.self_reported_confidence * 100)}%
                  </strong>
                </span>
              )}
            {(currentAgent.latency_ms || currentAgent.execution_time_ms) && (
              <span>⏱️ {Math.round(currentAgent.latency_ms || currentAgent.execution_time_ms)}ms</span>
            )}
          </div>
        </div>

        {isSuccess ? (
          <div className="text-sm leading-relaxed text-slate-700 dark:text-slate-300 space-y-2 whitespace-pre-wrap font-sans">
            {currentAgent.answer || currentAgent.content || "No detailed perspective provided."}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-semibold space-y-1">
            <p>
              ⚠️ This agent's response was unavailable:{" "}
              {currentAgent.error || currentAgent.error_message || "Execution timeout or API failure"}.
            </p>
            <p className="font-normal text-[11px] opacity-80">
              The Aggregator excluded this perspective and normalized weights across the remaining successful personas.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
