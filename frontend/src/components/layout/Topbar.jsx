import { useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import useUiStore from "../../store/uiStore";
import Button from "../ui/Button";

export default function Topbar() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme, toggleMobileDrawer } = useUiStore();
  const location = useLocation();

  const getPageInfo = (pathname) => {
    switch (pathname) {
      case "/":
      case "/documents":
        return {
          title: "Document Repository & RAG Ingestion",
          subtitle: "Upload, chunk, vectorize, and manage knowledge assets",
        };
      case "/chat":
        return {
          title: "Multi-Agent Query Engine",
          subtitle: "Collaborative reasoning and cited retrieval",
        };
      case "/history":
        return {
          title: "Session History & Audit Logs",
          subtitle: "Review past agent debates and query traces",
        };
      case "/settings":
        return {
          title: "Platform & Model Configuration",
          subtitle: "Adjust embedding models, LLM endpoints, and system parameters",
        };
      default:
        return {
          title: "Council of Minds",
          subtitle: "Advanced Agentic Artificial Intelligence Platform",
        };
    }
  };

  const pageInfo = getPageInfo(location.pathname);

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/60 backdrop-blur-xl px-4 sm:px-6 flex items-center justify-between z-30 sticky top-0 flex-shrink-0 gap-2">
      {/* Left side: Hamburger Menu (Mobile) + Page Title */}
      <div className="flex items-center gap-3 min-w-0 flex-1 mr-2">
        <button
          onClick={toggleMobileDrawer}
          className="lg:hidden w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 transition-all shadow-sm flex-shrink-0"
          title="Open Navigation Menu"
          aria-label="Open Navigation Menu"
        >
          ☰
        </button>
        <div className="flex flex-col min-w-0">
          <h1 className="text-sm sm:text-base font-bold text-slate-800 dark:text-slate-100 truncate">
            {pageInfo.title}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 truncate hidden sm:block font-normal">
            {pageInfo.subtitle}
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 transition-all shadow-sm flex-shrink-0"
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          aria-label="Toggle Theme"
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        {/* User Profile Badge */}
        {user && (
          <div className="flex items-center gap-2 sm:gap-3 bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 px-2.5 sm:px-3.5 py-1.5 rounded-2xl shadow-sm">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate max-w-[120px] md:max-w-[150px]">
                {user.full_name || user.email}
              </div>
            </div>
            <Button
              variant="danger"
              size="sm"
              onClick={logout}
              className="px-2.5 py-1 text-xs min-h-[36px]"
            >
              Sign Out
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
