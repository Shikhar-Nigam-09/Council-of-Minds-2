import React, { useState, useRef, useEffect } from "react";

export default function MessageInput({ onSend, disabled, onOpenWeightPanel, placeholder = "Ask the Council of Minds a question... (Shift+Enter for newline)" }) {
  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4 bg-white/80 dark:bg-slate-950/80 border-t border-slate-200 dark:border-slate-800/80 backdrop-blur-xl z-20">
      <div className="max-w-4xl mx-auto flex flex-col gap-2">
        {/* Toolbar above input */}
        {onOpenWeightPanel && (
          <div className="flex items-center justify-between px-1 text-xs">
            <button
              type="button"
              onClick={onOpenWeightPanel}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-indigo-600 dark:text-indigo-300 font-semibold border border-indigo-200 dark:border-indigo-800/60 transition-all text-xs min-h-[28px]"
              title="Adjust Persona Synthesis Weights"
            >
              <span>⚖️</span>
              <span>Agent Weights</span>
            </button>
            <span className="hidden sm:inline font-mono text-[10px] text-slate-400 dark:text-slate-500">
              Shift+Enter for newline
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
          <div className="relative flex-1 rounded-2xl bg-slate-100 dark:bg-slate-900/80 border border-slate-300 dark:border-slate-800 focus-within:border-indigo-500 dark:focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all overflow-hidden">
            <textarea
              ref={textareaRef}
              rows={1}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={placeholder}
              className="w-full bg-transparent p-3.5 pr-12 text-sm sm:text-base text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none resize-none max-h-48 leading-relaxed font-sans disabled:opacity-50"
            />
          </div>

          <button
            type="submit"
            disabled={!text.trim() || disabled}
            className="h-12 px-5 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 text-white font-bold text-sm shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-40 disabled:pointer-events-none flex items-center justify-center gap-1.5 flex-shrink-0"
            title="Send to Council (Enter)"
          >
            <span>Send</span>
            <span className="text-lg">→</span>
          </button>
        </form>
      </div>
    </div>
  );
}
