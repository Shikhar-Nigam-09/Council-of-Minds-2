import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { settingsApi } from "../api/settingsApi";
import { useAuthStore } from "../store/authStore";

export const useSettings = () => {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: settingsApi.getSettings,
    enabled: isAuthenticated,
  });

  const updateWeightsMutation = useMutation({
    mutationFn: (weights) => settingsApi.updateAgentWeights(weights),
    onMutate: async (newWeights) => {
      await queryClient.cancelQueries({ queryKey: ["settings"] });
      const previousSettings = queryClient.getQueryData(["settings"]);
      queryClient.setQueryData(["settings"], (old) =>
        old ? { ...old, agent_weights: newWeights } : old
      );
      return { previousSettings };
    },
    onError: (err, newWeights, context) => {
      if (context?.previousSettings) {
        queryClient.setQueryData(["settings"], context.previousSettings);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (fullName) => settingsApi.updateProfile(fullName),
    onMutate: async (newFullName) => {
      await queryClient.cancelQueries({ queryKey: ["settings"] });
      const previousSettings = queryClient.getQueryData(["settings"]);
      queryClient.setQueryData(["settings"], (old) =>
        old ? { ...old, full_name: newFullName } : old
      );
      return { previousSettings };
    },
    onError: (err, newFullName, context) => {
      if (context?.previousSettings) {
        queryClient.setQueryData(["settings"], context.previousSettings);
      }
    },
    onSuccess: (data) => {
      if (data && data.full_name !== undefined) {
        useAuthStore.getState().setUser({
          ...useAuthStore.getState().user,
          full_name: data.full_name,
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  return {
    settings: settingsQuery.data,
    isLoading: settingsQuery.isLoading,
    error: settingsQuery.error,
    refetch: settingsQuery.refetch,
    updateAgentWeights: updateWeightsMutation.mutateAsync,
    isUpdatingWeights: updateWeightsMutation.isPending,
    weightsError: updateWeightsMutation.error,
    updateProfile: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
    profileError: updateProfileMutation.error,
  };
};

export default useSettings;
