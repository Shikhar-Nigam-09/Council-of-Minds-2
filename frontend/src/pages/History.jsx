import { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import { useChats } from "../hooks/useChats";

export default function History() {
  const { chats, isLoading, error, deleteChat, isDeleting } = useChats();
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const navigate = useNavigate();

  const filteredAndSortedChats = useMemo(() => {
    if (!chats) return [];
    let list = [...chats];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (chat) =>
          chat.title?.toLowerCase().includes(q) ||
          chat.id?.toLowerCase().includes(q)
      );
    }

    list.sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at).getTime();
      const dateB = new Date(b.updated_at || b.created_at).getTime();
      return sortBy === "newest" ? dateB - dateA : dateA - dateB;
    });

    return list;
  }, [chats, searchQuery, sortBy]);

  const handleDelete = async (e, chatId) => {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this debate session and all its audit logs?")) {
      await deleteChat(chatId);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 py-6 sm:py-8 px-2 sm:px-4 min-w-0 break-words">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6 min-w-0">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <Badge variant="indigo" className="px-2.5 py-0.5 text-xs">
              Audit Archive
            </Badge>
            <span className="text-xs font-mono text-slate-400 dark:text-slate-500">
              {filteredAndSortedChats.length} Sessions Indexed
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white break-words">
            Session History & Audit Logs
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            Search past multi-agent debates, review consensus trends, and inspect chronological reasoning traces.
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <Link to="/chat" className="w-full md:w-auto">
            <Button variant="primary" className="shadow-lg shadow-indigo-500/20 w-full md:w-auto justify-center min-h-[40px]">
              <span>+ New Debate Session</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="p-3.5 sm:p-4 bg-slate-50/50 dark:bg-slate-900/50 backdrop-blur-md border-slate-200/80 dark:border-slate-800/80 min-w-0">
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-center justify-between">
          <div className="relative w-full sm:w-80">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              🔍
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search topic or ID..."
              className="w-full pl-9 pr-8 py-2.5 sm:py-2 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[40px]"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                ✕
              </button>
            )}
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              Sort by:
            </span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer min-h-[40px]"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Session List */}
      {isLoading ? (
        <div className="py-16 text-center space-y-4">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
            Loading audit archive...
          </p>
        </div>
      ) : error ? (
        <Card className="p-6 sm:p-8 text-center border-rose-500/20 bg-rose-500/5 space-y-3 min-w-0">
          <div className="text-3xl">⚠️</div>
          <h3 className="text-base font-bold text-rose-600 dark:text-rose-400">
            Failed to load session history
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto break-words">
            {error.message || "An error occurred while fetching your chat sessions."}
          </p>
        </Card>
      ) : filteredAndSortedChats.length === 0 ? (
        <Card className="p-8 sm:p-12 text-center border-slate-200 dark:border-slate-800 space-y-4 min-w-0">
          <div className="w-16 h-16 rounded-3xl bg-slate-100 dark:bg-slate-900 text-slate-400 flex items-center justify-center text-3xl mx-auto">
            📭
          </div>
          <div className="space-y-1 max-w-sm mx-auto">
            <h3 className="text-base sm:text-lg font-bold text-slate-800 dark:text-slate-200">
              {searchQuery ? "No matching sessions found" : "No debate history yet"}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              {searchQuery
                ? "Try adjusting your search query or clear filters."
                : "When you ask questions in the Chat Engine, all agent deliberations and citations will be archived here."}
            </p>
          </div>
          {!searchQuery && (
            <div className="pt-2">
              <Link to="/chat">
                <Button variant="primary" className="text-xs min-h-[36px] justify-center">
                  <span>Start Your First Debate</span>
                </Button>
              </Link>
            </div>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:gap-4">
          {filteredAndSortedChats.map((chat) => {
            const dateStr = new Date(chat.updated_at || chat.created_at).toLocaleDateString(
              undefined,
              { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" }
            );

            return (
              <div
                key={chat.id}
                onClick={() => navigate(`/chat/${chat.id}`)}
                className="group relative block rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/60 p-4 sm:p-5 shadow-sm hover:shadow-md hover:border-indigo-500/50 dark:hover:border-indigo-500/50 transition-all duration-200 cursor-pointer backdrop-blur-sm min-w-0 break-words"
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 min-w-0">
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap min-w-0">
                      <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse flex-shrink-0"></span>
                      <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors max-w-full">
                        {chat.title || "Untitled Debate Session"}
                      </h3>
                      <Badge variant="slate" className="text-[10px] font-mono px-2 py-0.5">
                        ID: {chat.id.slice(0, 8)}...
                      </Badge>
                    </div>

                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1 font-normal">
                      Last active on {dateStr}
                    </p>
                  </div>

                  <div className="flex items-center justify-end gap-2 w-full sm:w-auto flex-shrink-0 pt-2 sm:pt-0 border-t sm:border-0 border-slate-800/60">
                    <Button
                      variant="secondary"
                      size="sm"
                      className="text-xs opacity-90 sm:opacity-80 group-hover:opacity-100 transition-opacity flex-1 sm:flex-initial justify-center min-h-[36px]"
                    >
                      <span>Review Audit →</span>
                    </Button>
                    <button
                      onClick={(e) => handleDelete(e, chat.id)}
                      disabled={isDeleting}
                      className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                      title="Delete Session"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
