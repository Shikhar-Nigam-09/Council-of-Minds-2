import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useChat } from "../hooks/useChat";
import { useDocuments } from "../hooks/useDocuments";
import { useChatStore } from "../store/chatStore";
import MessageList from "../components/chat/MessageList";
import MessageInput from "../components/chat/MessageInput";
import AgentWeightPanel from "../components/chat/AgentWeightPanel";
import Spinner from "../components/ui/Spinner";

export default function Chat() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [isWeightPanelOpen, setIsWeightPanelOpen] = useState(false);
  const { chat, isLoading: isLoadingChat, sendMessage, isSending } = useChat(chatId);
  const { documents, isLoading: isLoadingDocs } = useDocuments();
  const { pendingQuestion, failedQuestion, clearFailedQuestion } = useChatStore();

  useEffect(() => {
    clearFailedQuestion();
  }, [chatId, clearFailedQuestion]);

  const handleSend = async (question) => {
    try {
      const res = await sendMessage({ question, chat_id: chatId });
      // Requirement 4: Navigate to /chat/{chatId} after backend creates chat
      if (!chatId && res?.chat_id) {
        navigate(`/chat/${res.chat_id}`);
      }
    } catch (err) {
      // Error is caught and stored in chatStore via useChat onError
      console.error("Message send error:", err);
    }
  };

  const messages = chat?.messages || [];

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] sm:h-[calc(100vh-7rem)] md:h-[calc(100vh-8rem)] min-h-[450px] bg-slate-50/50 dark:bg-slate-950/40 relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800">
      {/* Top Header */}
      <div className="px-3 sm:px-6 py-3 sm:py-3.5 bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800/80 backdrop-blur-xl flex items-center justify-between z-10 flex-shrink-0 shadow-sm gap-2">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold shadow-sm flex-shrink-0">
            💬
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-extrabold text-slate-800 dark:text-white truncate">
              {chat?.title || (chatId ? "Debate Session" : "New Debate Session")}
            </h2>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">
              {chatId ? `Session ID: ${chatId.slice(0, 8)}...` : "Client-Side Session (Not Persisted Yet)"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => setIsWeightPanelOpen(true)}
            className="px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/60 hover:bg-purple-100 dark:hover:bg-purple-900/80 text-purple-600 dark:text-purple-300 text-xs font-bold transition-all border border-purple-200 dark:border-purple-800/60 flex items-center gap-1.5 min-h-[36px]"
            title="Adjust Persona Synthesis Weights"
          >
            <span>⚖️</span>
            <span className="hidden sm:inline">Agent Weights</span>
          </button>

          {chatId && (
            <Link
              to="/chat"
              className="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900/80 text-indigo-600 dark:text-indigo-300 text-xs font-bold transition-all border border-indigo-200 dark:border-indigo-800/60 flex items-center gap-1.5 min-h-[36px]"
            >
              <span>+ New Debate</span>
            </Link>
          )}
        </div>
      </div>

      {/* Message List Area */}
      {isLoadingChat ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400">
          <Spinner size="lg" />
          <span className="text-xs font-mono">Loading debate history...</span>
        </div>
      ) : (
        <MessageList
          messages={messages}
          pendingQuestion={pendingQuestion}
          failedQuestion={failedQuestion}
          onRetry={handleSend}
          isRetrying={isSending}
          documents={documents}
          isLoadingDocs={isLoadingDocs}
        />
      )}

      {/* Bottom Message Input */}
      <MessageInput
        onSend={handleSend}
        disabled={isSending || Boolean(pendingQuestion)}
        onOpenWeightPanel={() => setIsWeightPanelOpen(true)}
      />

      {/* Inline Agent Weights Drawer / Sheet */}
      <AgentWeightPanel
        isOpen={isWeightPanelOpen}
        onClose={() => setIsWeightPanelOpen(false)}
      />
    </div>
  );
}
