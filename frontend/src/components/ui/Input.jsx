/* eslint-disable react/prop-types */
import { forwardRef } from "react";

const Input = forwardRef(
  (
    {
      label = null,
      helperText = null,
      error = null,
      icon = null,
      className = "",
      id,
      type = "text",
      ...props
    },
    ref,
  ) => {
    const inputId =
      id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full flex flex-col space-y-1.5 text-left">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-semibold text-slate-700 dark:text-slate-300 tracking-wide uppercase"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            type={type}
            className={`w-full rounded-xl px-4 py-2.5 text-base sm:text-sm min-h-[42px] transition-all duration-200 outline-none border shadow-sm ${
              icon ? "pl-10" : ""
            } ${
              error
                ? "bg-rose-500/5 border-rose-500/80 text-rose-900 dark:text-rose-200 placeholder-rose-400/60 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500"
                : "bg-white dark:bg-slate-950/80 border-slate-300 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 hover:border-slate-400 dark:hover:border-slate-700"
            } ${className}`}
            {...props}
          />
        </div>
        {error && (
          <p className="text-xs text-rose-500 dark:text-rose-400 font-medium animate-pulse">
            {error}
          </p>
        )}
        {!error && helperText && (
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {helperText}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";

export default Input;
