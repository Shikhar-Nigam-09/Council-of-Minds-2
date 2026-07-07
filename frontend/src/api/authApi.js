import { apiClient } from "./client";

export const authApi = {
  register: async (data) => {
    const response = await apiClient.post("/api/v1/auth/register", data);
    return response.data;
  },

  login: async (credentials) => {
    const response = await apiClient.post("/api/v1/auth/login", credentials);
    return response.data;
  },

  refresh: async (refreshToken) => {
    const response = await apiClient.post("/api/v1/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getMe: async () => {
    const response = await apiClient.get("/api/v1/auth/me");
    return response.data;
  },

  changePassword: async (data) => {
    const response = await apiClient.post("/api/v1/auth/change-password", data);
    return response.data;
  },
};

export default authApi;
