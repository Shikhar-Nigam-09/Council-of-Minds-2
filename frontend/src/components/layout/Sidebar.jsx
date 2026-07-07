import { useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import useUiStore from "../../store/uiStore";
import { useChats } from "../../hooks/useChats";

export default function Sidebar() {
  const {
    sidebarCollapsed,
    toggleSidebar,
    mobileDrawerOpen,
    closeMobileDrawer,
  } = useUiStore();
  const location = useLocation();
  const navigate = useNavigate();
  const { chats, isLoading: isLoadingChats, deleteChat, isDeleting } = useChats();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && mobileDrawerOpen) {
        closeMobileDrawer();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mobileDrawerOpen, closeMobileDrawer]);

  const navItems = [
    {
      name: "Documents",
      path: "/documents",
      icon: "📂",
      description: "RAG Vector Repository",
      badge: null,
    },
    {
      name: "Chat Engine",
      path: "/chat",
      icon: "💬",
      description: "Multi-Agent Query Hub",
      badge: null,
    },
    {
      name: "History",
      path: "/history",
      icon: "📜",
      description: "Past Sessions & Logs",
      badge: null,
    },
    {
      name: "Settings",
      path: "/settings",
      icon: "⚙️",
      description: "Platform & Model Config",
      badge: null,
    },
  ];

  const isActive = (path) => {
    if (
      path === "/documents" &&
      (location.pathname === "/" ||
        location.pathname === "/documents" ||
        location.pathname.startsWith("/documents/"))
    ) {
      return true;
    }
    if (path === "/chat" && location.pathname.startsWith("/chat")) {
      return true;
    }
    return location.pathname === path;
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-200 dark:border-slate-800/80 bg-white/95 dark:bg-slate-950/95 backdrop-blur-xl transition-all duration-300 flex-shrink-0 w-72 h-full shadow-2xl lg:shadow-none lg:static lg:h-auto lg:bg-white/80 lg:dark:bg-slate-950/60 lg:z-40 ${
        mobileDrawerOpen
          ? "translate-x-0"
          : "-translate-x-full lg:translate-x-0"
      } ${sidebarCollapsed ? "lg:w-20" : "lg:w-64"}`}
    >
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between h-16">
        <Link
          to="/"
          onClick={closeMobileDrawer}
          className="flex items-center gap-3 overflow-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20 flex-shrink-0 text-base">
            CM
          </div>
          {!sidebarCollapsed && (
            <div className="flex flex-col min-w-0 transition-opacity duration-200">
              <span className="font-extrabold text-sm tracking-tight bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-800 dark:from-white dark:via-slate-200 dark:to-slate-400 bg-clip-text text-transparent truncate">
                Council of Minds
              </span>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={closeMobileDrawer}
              className={`group flex items-center gap-3.5 px-3.5 py-3 rounded-2xl transition-all duration-200 relative ${
                active
                  ? "bg-gradient-to-r from-indigo-500/15 via-purple-500/10 to-transparent dark:from-indigo-500/20 dark:via-purple-500/10 text-indigo-900 dark:text-white font-bold border-l-4 border-indigo-500 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-slate-200 font-medium"
              }`}
              title={
                sidebarCollapsed
                  ? `${item.name} (${item.description})`
                  : undefined
              }
            >
              <span className="text-xl flex-shrink-0 transition-transform group-hover:scale-110">
                {item.icon}
              </span>
              {!sidebarCollapsed && (
                <div className="flex flex-col min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-sm truncate">{item.name}</span>
                    {item.badge && (
                      <span className="px-1.5 py-0.5 rounded-md bg-purple-500/10 dark:bg-purple-500/20 text-[9px] font-mono font-semibold text-purple-600 dark:text-purple-400 border border-purple-500/20">
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-slate-400 dark:text-slate-500 truncate font-normal">
                    {item.description}
                  </span>
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Recent Debates Switcher */}
      {!sidebarCollapsed && (
        <div className="p-3 border-t border-slate-200 dark:border-slate-800/80 flex flex-col gap-2 max-h-56 overflow-y-auto">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Recent Debates
            </span>
            <Link
              to="/chat"
              onClick={closeMobileDrawer}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center gap-1 bg-indigo-50 dark:bg-indigo-950/50 px-2.5 py-1 rounded-md border border-indigo-200 dark:border-indigo-800/60 min-h-[32px]"
              title="Start New Debate"
            >
              <span>+ New</span>
            </Link>
          </div>
          {isLoadingChats ? (
            <div className="text-xs text-slate-400 p-2 text-center">
              Loading sessions...
            </div>
          ) : chats.length === 0 ? (
            <div className="text-xs text-slate-400 dark:text-slate-500 p-2 text-center italic">
              No active sessions yet.
            </div>
          ) : (
            <div className="space-y-1">
              {chats.map((chat) => {
                const isCurrent = location.pathname === `/chat/${chat.id}`;
                return (
                  <div
                    key={chat.id}
                    className={`group flex items-center justify-between gap-2 px-2.5 py-2 rounded-xl text-xs transition-all ${
                      isCurrent
                        ? "bg-indigo-500/10 text-indigo-900 dark:text-indigo-200 font-semibold border-l-2 border-indigo-500"
                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    <Link
                      to={`/chat/${chat.id}`}
                      onClick={closeMobileDrawer}
                      className="truncate flex-1 min-w-0 py-0.5"
                      title={chat.title || "Untitled Debate"}
                    >
                      {chat.title || "Untitled Debate"}
                    </Link>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        if (window.confirm("Delete this debate session?")) {
                          deleteChat(chat.id);
                          if (isCurrent) navigate("/chat");
                        }
                      }}
                      disabled={isDeleting}
                      className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-500 transition-opacity p-1.5 min-h-[28px] min-w-[28px] flex items-center justify-center"
                      title="Delete session"
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Collapse / Close Toggle Button */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-800/80 flex items-center justify-end gap-2">
        <button
          onClick={closeMobileDrawer}
          className="lg:hidden w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-900/80 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all text-xs font-semibold"
          title="Close Menu"
        >
          <span>✕</span>
          <span>Close Menu</span>
        </button>
        <button
          onClick={toggleSidebar}
          className="hidden lg:flex w-full items-center justify-center gap-2 px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-900/80 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all text-xs font-semibold"
          title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          <span>{sidebarCollapsed ? "→" : "←"}</span>
          {!sidebarCollapsed && <span>Collapse Sidebar</span>}
        </button>
      </div>
    </aside>
  );
}
