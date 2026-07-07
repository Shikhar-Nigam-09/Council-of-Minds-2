import React, { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import UserMessage from "./UserMessage";
import AssistantMessage from "./AssistantMessage";
import CouncilLoadingState from "./CouncilLoadingState";

export default function MessageList({
  messages = [],
  pendingQuestion,
  failedQuestion,
  onRetry,
  isRetrying,
  documents = [],
  isLoadingDocs,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, pendingQuestion, failedQuestion]);

  // Determine Document State (Requirement 2)
  const totalDocs = documents.length;
  const readyDocs = documents.filter((d) => d.status === "ready").length;
  const processingDocs = documents.filter(
    (d) => d.status === "processing" || d.status === "uploaded"
  ).length;
  const failedDocs = documents.filter((d) => d.status === "failed").length;

  let docBanner = null;
  if (!isLoadingDocs) {
    if (totalDocs === 0) {
      docBanner = (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-900 dark:text-amber-200 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            <span className="text-xl flex-shrink-0">⚠️</span>
            <div className="min-w-0">
              <h5 className="text-xs font-bold uppercase tracking-wider truncate">
                No Indexed Documents in Repository
              </h5>
              <p className="text-xs opacity-90 break-words">
                Upload PDF or TXT files to provide knowledge for the Council of Minds to query and synthesize.
              </p>
            </div>
          </div>
          <Link
            to="/documents"
            className="px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold transition-all shadow-sm whitespace-nowrap min-h-[36px] flex items-center justify-center"
          >
            📂 Upload Documents
          </Link>
        </div>
      );
    } else if (readyDocs === 0 && processingDocs > 0) {
      docBanner = (
        <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-900 dark:text-blue-200 flex items-center gap-2.5 min-w-0">
          <span className="text-xl animate-spin flex-shrink-0">⏳</span>
          <div className="min-w-0">
            <h5 className="text-xs font-bold uppercase tracking-wider truncate">
              Documents Currently Processing ({processingDocs})
            </h5>
            <p className="text-xs opacity-90 break-words">
              Text extraction and vector embedding generation are in progress. You can query once processing completes.
            </p>
          </div>
        </div>
      );
    } else if (readyDocs === 0 && failedDocs > 0) {
      docBanner = (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-900 dark:text-rose-200 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            <span className="text-xl flex-shrink-0">❌</span>
            <div className="min-w-0">
              <h5 className="text-xs font-bold uppercase tracking-wider truncate">
                All Uploaded Documents Failed Ingestion
              </h5>
              <p className="text-xs opacity-90 break-words">
                Please review document errors or retry ingestion in your repository.
              </p>
            </div>
          </div>
          <Link
            to="/documents"
            className="px-3 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-bold transition-all shadow-sm whitespace-nowrap min-h-[36px] flex items-center justify-center"
          >
            📂 Check Repository
          </Link>
        </div>
      );
    }
  }

  const isEmpty = messages.length === 0 && !pendingQuestion && !failedQuestion;

  return (
    <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 sm:p-6 space-y-6 min-w-0">
      <div className="max-w-4xl mx-auto space-y-6 min-w-0 w-full">
        {/* Document State Banner */}
        {docBanner}

        {/* Empty Welcome Screen */}
        {isEmpty && (
          <div className="py-12 text-center space-y-6 animate-fade-in px-2">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-white flex items-center justify-center text-3xl mx-auto shadow-xl shadow-indigo-500/20 animate-float">
              💬
            </div>
            <div className="space-y-2 max-w-md mx-auto">
              <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
                Council Debate Chamber Ready
              </h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed break-words">
                Ask a question below. Five specialized AI agents (Logical, Rational, Practical, Spiritual, Skeptical) will query your vector repository, debate hypotheses, and synthesize an explainable, cited conclusion.
              </p>
            </div>
          </div>
        )}

        {/* Chronological Messages */}
        {messages.map((msg, idx) => {
          if (msg.role === "user") {
            return (
              <UserMessage
                key={msg.id || idx}
                message={msg}
                onRetry={onRetry}
                isRetrying={isRetrying}
              />
            );
          }
          return <AssistantMessage key={msg.id || idx} message={msg} />;
        })}

        {/* Optimistic Deliberation State */}
        {pendingQuestion && (
          <>
            <UserMessage message={{ content: pendingQuestion, role: "user" }} />
            <div className="max-w-3xl min-w-0 w-full">
              <CouncilLoadingState />
            </div>
          </>
        )}

        {/* Failed Submission State */}
        {failedQuestion && (
          <UserMessage
            message={{
              content: failedQuestion.question,
              role: "user",
              status: "failed",
              error: failedQuestion.error,
            }}
            onRetry={onRetry}
            isRetrying={isRetrying}
          />
        )}

        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
}
