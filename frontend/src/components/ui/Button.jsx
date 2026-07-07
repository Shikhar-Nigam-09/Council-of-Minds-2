/* eslint-disable react/prop-types */
import Spinner from "./Spinner";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled = false,
  icon = null,
  className = "",
  ...props
}) {
  const baseStyles =
    "inline-flex items-center justify-center font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none break-words max-w-full";

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs rounded-xl gap-1.5 min-h-[32px]",
    md: "px-4 py-2 text-sm rounded-xl gap-2 min-h-[38px]",
    lg: "px-6 py-3 text-base rounded-2xl gap-2.5 min-h-[44px]",
  };

  const variantStyles = {
    primary:
      "bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white shadow-lg shadow-indigo-500/20 hover:opacity-95 hover:shadow-indigo-500/30 border border-white/10",
    secondary:
      "bg-slate-200 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/80 text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700/80 shadow-sm",
    danger:
      "bg-rose-500/10 text-rose-500 dark:text-rose-400 hover:bg-rose-500/20 border border-rose-500/20 shadow-sm",
    outline:
      "border border-indigo-500/50 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/10 shadow-sm",
    ghost:
      "text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white",
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`${baseStyles} ${sizeStyles[size] || sizeStyles.md} ${
        variantStyles[variant] || variantStyles.primary
      } ${className}`}
      {...props}
    >
      {isLoading && <Spinner size="sm" className="text-current animate-spin" />}
      {!isLoading && icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
}
