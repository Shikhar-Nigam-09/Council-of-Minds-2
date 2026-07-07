/* eslint-disable react/prop-types */
export default function Card({
  children,
  header = null,
  footer = null,
  className = "",
  headerClassName = "",
  bodyClassName = "",
  footerClassName = "",
  ...props
}) {
  return (
    <div
      className={`backdrop-blur-xl bg-white/80 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 rounded-3xl overflow-hidden shadow-xl shadow-slate-200/50 dark:shadow-black/50 transition-all duration-300 min-w-0 break-words max-w-full ${className}`}
      {...props}
    >
      {header && (
        <div
          className={`px-4 sm:px-6 py-3.5 sm:py-4 border-b border-slate-200/80 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/40 flex items-center justify-between min-w-0 ${headerClassName}`}
        >
          {header}
        </div>
      )}
      <div className={`p-4 sm:p-6 min-w-0 break-words ${bodyClassName}`}>{children}</div>
      {footer && (
        <div
          className={`px-4 sm:px-6 py-3.5 sm:py-4 border-t border-slate-200/80 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/40 min-w-0 ${footerClassName}`}
        >
          {footer}
        </div>
      )}
    </div>
  );
}
