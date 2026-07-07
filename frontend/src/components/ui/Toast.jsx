import { useEffect } from "react";
import useUiStore from "../../store/uiStore";

/* eslint-disable react/prop-types */
function ToastItem({ toast, onRemove }) {
  const { id, title, message, type = "info", duration = 4000 } = toast;

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onRemove(id);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onRemove]);

  const typeStyles = {
    success:
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-900 dark:text-emerald-100",
    error: "border-rose-500/30 bg-rose-500/10 text-rose-900 dark:text-rose-100",
    warning:
      "border-amber-500/30 bg-amber-500/10 text-amber-900 dark:text-amber-100",
    info: "border-indigo-500/30 bg-indigo-500/10 text-indigo-900 dark:text-indigo-100",
  };

  const icons = {
    success: "✓",
    error: "✕",
    warning: "!",
    info: "i",
  };

  const iconBg = {
    success: "bg-emerald-500 text-white",
    error: "bg-rose-500 text-white",
    warning: "bg-amber-500 text-white",
    info: "bg-indigo-500 text-white",
  };

  return (
    <div
      className={`pointer-events-auto backdrop-blur-2xl bg-white/95 dark:bg-slate-900/95 border rounded-2xl p-4 shadow-2xl shadow-black/30 transition-all animate-in slide-in-from-right-5 fade-in duration-300 flex items-start gap-3.5 ${
        typeStyles[type] || typeStyles.info
      }`}
      role="alert"
    >
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5 shadow-sm ${
          iconBg[type] || iconBg.info
        }`}
      >
        {icons[type] || icons.info}
      </div>
      <div className="flex-1 min-w-0">
        {title && <h4 className="text-sm font-bold leading-tight">{title}</h4>}
        {message && (
          <p className="text-xs opacity-90 mt-1 leading-relaxed break-words">
            {message}
          </p>
        )}
      </div>
      <button
        onClick={() => onRemove(id)}
        className="text-slate-400 hover:text-slate-600 dark:hover:text-white p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
        aria-label="Close toast"
      >
        ✕
      </button>
    </div>
  );
}

export default function Toast() {
  const { toasts, removeToast } = useUiStore();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 z-50 flex flex-col gap-3 max-w-full sm:max-w-sm sm:w-96 pointer-events-none p-1">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
      ))}
    </div>
  );
}
