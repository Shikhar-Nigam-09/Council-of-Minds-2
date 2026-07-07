import React from "react";
import { useChatStore } from "../../store/chatStore";
import ConfidenceMeter from "./ConfidenceMeter";
import ConfidenceBreakdownPanel from "./ConfidenceBreakdownPanel";
import AgentResponsePanel from "./AgentResponsePanel";
import ChallengerPanel from "./ChallengerPanel";
import EvidencePanel from "./EvidencePanel";

export default function AssistantMessage({ message }) {
  const { expandedPanels, togglePanel } = useChatStore();
  const panels = expandedPanels[message.id || "temp"] || {
    breakdown: false,
    agents: false,
    challenger: false,
    evidence: false,
  };

  const challengerResp = message.agent_responses?.find(
    (a) => a.agent_name && a.agent_name.toLowerCase() === "challenger"
  );
  const reasoningCount =
    message.agent_responses?.filter(
      (a) => a.agent_name && a.agent_name.toLowerCase() !== "challenger"
    ).length || 0;
  const evidenceCount = message.evidence?.length || 0;

  return (
    <div className="flex items-start gap-2 sm:gap-3.5 max-w-3xl animate-fade-in w-full min-w-0">
      {/* Avatar */}
      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 flex-shrink-0 text-xs sm:text-sm mt-1 sm:mt-0">
        CM
      </div>

      {/* Message Body */}
      <div className="flex-1 space-y-4 min-w-0 bg-white/80 dark:bg-slate-900/80 p-4 sm:p-6 rounded-2xl sm:rounded-3xl rounded-tl-sm border border-slate-200/80 dark:border-slate-800/80 shadow-sm backdrop-blur-xl break-words">
        {/* Synthesized Final Answer */}
        <div className="text-sm sm:text-base leading-relaxed text-slate-800 dark:text-slate-100 font-sans whitespace-pre-wrap break-words overflow-wrap-anywhere">
          {message.content}
        </div>

        {/* Confidence Meter */}
        {message.confidence_score !== null && message.confidence_score !== undefined && (
          <div className="pt-2 min-w-0">
            <ConfidenceMeter
              score={message.confidence_score}
              onToggleBreakdown={() => togglePanel(message.id || "temp", "breakdown")}
              isBreakdownExpanded={panels.breakdown}
            />
          </div>
        )}

        {/* Confidence Breakdown Panel */}
        {panels.breakdown && message.confidence_breakdown && (
          <ConfidenceBreakdownPanel breakdown={message.confidence_breakdown} />
        )}

        {/* Collapsible Action Buttons */}
        <div className="pt-3 border-t border-slate-200 dark:border-slate-800/80 flex items-center flex-wrap gap-2">
          {reasoningCount > 0 && (
            <button
              onClick={() => togglePanel(message.id || "temp", "agents")}
              className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all border flex-1 sm:flex-initial min-h-[36px] ${
                panels.agents
                  ? "bg-indigo-500 text-white border-indigo-600 shadow-sm"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              <span>🤖</span>
              <span>5 Reasoning Perspectives</span>
              <span>{panels.agents ? "▲" : "▼"}</span>
            </button>
          )}

          {challengerResp && (
            <button
              onClick={() => togglePanel(message.id || "temp", "challenger")}
              className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all border flex-1 sm:flex-initial min-h-[36px] ${
                panels.challenger
                  ? "bg-rose-500 text-white border-rose-600 shadow-sm"
                  : "bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800/60 hover:bg-rose-100 dark:hover:bg-rose-900/60"
              }`}
            >
              <span>🛡️</span>
              <span>Challenger Critique</span>
              <span>{panels.challenger ? "▲" : "▼"}</span>
            </button>
          )}

          <button
            onClick={() => togglePanel(message.id || "temp", "evidence")}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all border flex-1 sm:flex-initial min-h-[36px] ${
              panels.evidence
                ? "bg-teal-600 text-white border-teal-700 shadow-sm"
                : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700"
            }`}
          >
            <span>📚</span>
            <span>Retrieved Evidence ({evidenceCount})</span>
            <span>{panels.evidence ? "▲" : "▼"}</span>
          </button>
        </div>

        {/* Collapsible Panels */}
        {panels.agents && message.agent_responses && (
          <div className="pt-2">
            <AgentResponsePanel agentResponses={message.agent_responses} />
          </div>
        )}

        {panels.challenger && challengerResp && (
          <div className="pt-2">
            <ChallengerPanel challengerResponse={challengerResp} />
          </div>
        )}

        {panels.evidence && (
          <div className="pt-2">
            <EvidencePanel evidence={message.evidence || []} />
          </div>
        )}
      </div>
    </div>
  );
}
