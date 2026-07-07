/* eslint-disable react/prop-types */
import { useEffect } from "react";
import { createPortal } from "react-dom";

export default function Modal({
  isOpen = false,
  onClose,
  title = null,
  children,
  footer = null,
  maxWidth = "md",
  className = "",
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose && onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen || typeof document === "undefined") return null;

  const maxWidthStyles = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
      {/* Backdrop overlay */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div
        className={`relative w-[95%] sm:w-full ${
          maxWidthStyles[maxWidth] || maxWidthStyles.md
        } max-h-[88vh] flex flex-col backdrop-blur-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl sm:rounded-3xl shadow-2xl shadow-black/80 overflow-hidden z-10 animate-in fade-in zoom-in-95 duration-200 ${className}`}
      >
        {/* Header */}
        {(title || onClose) && (
          <div className="px-4 sm:px-6 py-3.5 sm:py-4 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/40 flex-shrink-0">
            {title && (
              <h3 className="text-sm sm:text-base font-bold text-slate-800 dark:text-slate-200 truncate pr-2">
                {title}
              </h3>
            )}
            {onClose && (
              <button
                onClick={onClose}
                className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors flex-shrink-0 min-h-[32px] min-w-[32px]"
                aria-label="Close modal"
              >
                ✕
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="p-4 sm:p-6 text-slate-700 dark:text-slate-300 overflow-y-auto min-h-0 flex-1 break-words">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="px-4 sm:px-6 py-3.5 sm:py-4 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/40 flex flex-wrap items-center justify-end gap-2 sm:gap-3 flex-shrink-0">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
