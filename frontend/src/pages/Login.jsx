import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const { login, isLoggingIn } = useAuth();
  const [searchParams] = useSearchParams();

  const isRegistered = searchParams.get("registered") === "true";
  const isExpired = searchParams.get("expired") === "true";
  const isInvalidated = searchParams.get("invalidated") === "true";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      await login({ email, password });
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail ||
          "Failed to sign in. Please check your credentials.",
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-3 sm:p-4 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none animate-pulse delay-1000" />

      <div className="max-w-md w-full backdrop-blur-2xl bg-slate-900/70 border border-slate-800/80 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-black/80 relative z-10 transition-all duration-300 hover:border-slate-700/80 min-w-0 break-words">
        <div className="text-center mb-6 sm:mb-8 min-w-0">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30 mb-4 font-bold text-xl text-white">
            CM
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent break-words">
            Welcome Back
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-2">
            Sign in to access your Council of Minds workspace
          </p>
        </div>

        {/* Status messages */}
        {isRegistered && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs sm:text-sm flex items-center gap-3 break-words">
            <span className="text-lg flex-shrink-0">✓</span>
            <span>Registration successful! Please sign in below.</span>
          </div>
        )}
        {isExpired && (
          <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs sm:text-sm flex items-center gap-3 break-words">
            <span className="text-lg flex-shrink-0">⚠</span>
            <span>Your session has expired. Please sign in again.</span>
          </div>
        )}
        {isInvalidated && (
          <div className="mb-6 p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs sm:text-sm flex items-center gap-3 break-words">
            <span className="text-lg flex-shrink-0">🛡</span>
            <span>
              Password changed successfully. All previous sessions invalidated.
            </span>
          </div>
        )}
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-center gap-3 break-words">
            <span className="text-lg flex-shrink-0">✕</span>
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 min-w-0">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 sm:mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-2.5 sm:py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-base sm:text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all min-h-[44px]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 sm:mb-2">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-2.5 sm:py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-base sm:text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all min-h-[44px]"
            />
          </div>

          <button
            type="submit"
            disabled={isLoggingIn}
            className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 text-white font-semibold shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none transition-all duration-200 flex items-center justify-center gap-2 min-h-[44px]"
          >
            {isLoggingIn ? (
              <>
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Signing in...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center text-sm text-slate-400">
          Don&apos;t have an account?{" "}
          <Link
            to="/register"
            className="text-indigo-400 font-semibold hover:text-indigo-300 transition-colors"
          >
            Create one now
          </Link>
        </div>
      </div>
    </div>
  );
}
