import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api/authApi";
import { useAuthStore } from "../store/authStore";

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const {
    accessToken,
    user,
    isAuthenticated,
    login: storeLogin,
    logout: storeLogout,
  } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: async (credentials) => {
      const tokenData = await authApi.login(credentials);
      return tokenData;
    },
    onSuccess: async (tokenData) => {
      useAuthStore
        .getState()
        .setTokens(tokenData.access_token, tokenData.refresh_token);
      try {
        const userData = await authApi.getMe();
        storeLogin(tokenData.access_token, tokenData.refresh_token, userData);
        navigate("/");
      } catch (err) {
        storeLogout();
        throw err;
      }
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (data) => {
      const userData = await authApi.register(data);
      return userData;
    },
    onSuccess: () => {
      navigate("/login?registered=true");
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: async (data) => {
      return await authApi.changePassword(data);
    },
    onSuccess: () => {
      storeLogout();
      queryClient.clear();
      navigate("/login?invalidated=true");
    },
  });

  const logout = () => {
    storeLogout();
    queryClient.clear();
    navigate("/login");
  };

  const userQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const data = await authApi.getMe();
      useAuthStore.getState().setUser(data);
      return data;
    },
    enabled: isAuthenticated && !!accessToken,
    retry: false,
  });

  return {
    user: user || userQuery.data,
    isLoadingUser: userQuery.isLoading,
    isAuthenticated,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    changePassword: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
    changePasswordError: changePasswordMutation.error,
    logout,
  };
}

export default useAuth;
