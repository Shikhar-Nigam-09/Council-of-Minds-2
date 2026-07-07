import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "../api/chatApi";

export const useChats = () => {
  const queryClient = useQueryClient();

  const chatsQuery = useQuery({
    queryKey: ["chats"],
    queryFn: chatApi.listChats,
    staleTime: 1000 * 60 * 5, // 5 minutes stale time
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => chatApi.deleteChat(id),
    onMutate: async (deletedId) => {
      await queryClient.cancelQueries({ queryKey: ["chats"] });
      const previousChats = queryClient.getQueryData(["chats"]);
      queryClient.setQueryData(["chats"], (old = []) =>
        old.filter((chat) => chat.id !== deletedId)
      );
      return { previousChats };
    },
    onError: (err, deletedId, context) => {
      if (context?.previousChats) {
        queryClient.setQueryData(["chats"], context.previousChats);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["chats"] });
    },
  });

  return {
    chats: chatsQuery.data || [],
    isLoading: chatsQuery.isLoading,
    error: chatsQuery.error,
    refetch: chatsQuery.refetch,
    deleteChat: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
};
