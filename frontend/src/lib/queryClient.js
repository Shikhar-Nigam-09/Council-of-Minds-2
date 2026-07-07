import { QueryClient } from "@tanstack/react-query";

/**
 * Centralized TanStack Query client configuration with sane defaults.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes default stale time
    },
    mutations: {
      retry: 0,
    },
  },
});

export default queryClient;
