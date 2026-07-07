import React from "react";

export default function UserMessage({ message, onRetry, isRetrying }) {
  const isFailed = message.status === "failed" || Boolean(message.error);

  return (
    <div className="flex flex-col items-end space-y-1.5 animate-fade-in w-full min-w-0">
      <div className="flex items-center gap-2 max-w-[92%] sm:max-w-[75%] min-w-0">
        <div
          className={`p-3.5 sm:p-4 rounded-2xl sm:rounded-3xl rounded-tr-sm text-sm sm:text-base leading-relaxed font-sans shadow-md min-w-0 break-words overflow-wrap-anywhere ${
            isFailed
              ? "bg-rose-500/10 border-2 border-rose-500 text-rose-950 dark:text-rose-100"
              : "bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 text-white shadow-indigo-500/20"
          }`}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>

      {isFailed && (
        <div className="flex flex-wrap items-center justify-end gap-2 px-2 text-xs text-rose-600 dark:text-rose-400 font-semibold max-w-full">
          <span>⚠️ Message failed to evaluate: {message.error || "Council evaluation error"}</span>
          {onRetry && (
            <button
              onClick={() => onRetry(message.content)}
              disabled={isRetrying}
              className="px-3 py-1.5 rounded-xl bg-rose-500 hover:bg-rose-600 text-white font-bold transition-all shadow-sm disabled:opacity-50 flex items-center gap-1 min-h-[32px]"
            >
              <span>{isRetrying ? "Retrying..." : "↻ Retry"}</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
