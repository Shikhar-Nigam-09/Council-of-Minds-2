/* eslint-disable react/prop-types */
export default function Badge({
  children,
  variant = "default",
  dot = null,
  className = "",
  ...props
}) {
  const variantStyles = {
    success:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20",
    uploaded:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20",
    warning:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20",
    processing:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20",
    info: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20",
    ready:
      "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20",
    error:
      "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20",
    failed:
      "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20",
    deletion_failed:
      "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20",
    purple:
      "bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20",
    default:
      "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700",
  };

  const dotColors = {
    success: "bg-emerald-500 dark:bg-emerald-400",
    uploaded: "bg-emerald-500 dark:bg-emerald-400",
    warning: "bg-amber-500 dark:bg-amber-400",
    processing: "bg-amber-500 dark:bg-amber-400",
    info: "bg-indigo-500 dark:bg-indigo-400",
    ready: "bg-indigo-500 dark:bg-indigo-400",
    error: "bg-rose-500 dark:bg-rose-400",
    failed: "bg-rose-500 dark:bg-rose-400",
    deletion_failed: "bg-rose-500 dark:bg-rose-400",
    purple: "bg-purple-500 dark:bg-purple-400",
    default: "bg-slate-500 dark:bg-slate-400",
  };

  const dotAnimation =
    dot === "pulse" || dot === true
      ? "animate-pulse"
      : dot === "spin"
        ? "animate-spin"
        : "";

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold transition-colors ${
        variantStyles[variant] || variantStyles.default
      } ${className}`}
      {...props}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            dotColors[variant] || dotColors.default
          } ${dotAnimation}`}
        />
      )}
      <span>{children}</span>
    </span>
  );
}
