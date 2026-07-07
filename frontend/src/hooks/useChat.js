import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "../api/chatApi";
import { useChatStore } from "../store/chatStore";

export const useChat = (chatId) => {
  const queryClient = useQueryClient();
  const { startDeliberation, stopDeliberation, setFailedQuestion } = useChatStore();

  const chatQuery = useQuery({
    queryKey: ["chat", chatId],
    queryFn: () => chatApi.getChat(chatId),
    enabled: Boolean(chatId),
    staleTime: 1000 * 60, // 1 minute
  });

  const sendMutation = useMutation({
    mutationFn: ({ question, chat_id, agent_weights }) =>
      chatApi.sendMessage({ question, chat_id, agent_weights }),
    onMutate: async ({ question }) => {
      startDeliberation(question);
    },
    onSuccess: (data, variables) => {
      stopDeliberation();
      queryClient.invalidateQueries({ queryKey: ["chats"] });
      if (variables.chat_id) {
        queryClient.invalidateQueries({ queryKey: ["chat", variables.chat_id] });
      }
    },
    onError: (err, variables) => {
      const errorMsg =
        err?.response?.data?.detail || err?.message || "Council evaluation failed.";
      setFailedQuestion({
        question: variables.question,
        chat_id: variables.chat_id || null,
        error: errorMsg,
      });
      if (variables.chat_id) {
        queryClient.invalidateQueries({ queryKey: ["chat", variables.chat_id] });
      }
    },
  });

  return {
    chat: chatQuery.data || null,
    isLoading: chatQuery.isLoading,
    error: chatQuery.error,
    refetch: chatQuery.refetch,
    sendMessage: sendMutation.mutateAsync,
    isSending: sendMutation.isPending,
  };
};
