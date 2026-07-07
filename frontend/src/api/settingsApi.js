import { apiClient } from "./client";

export const settingsApi = {
  getSettings: async () => {
    const response = await apiClient.get("/api/v1/settings");
    return response.data;
  },

  updateAgentWeights: async (weights) => {
    const response = await apiClient.patch("/api/v1/settings/agent-weights", {
      agent_weights: weights,
    });
    return response.data;
  },

  updateProfile: async (fullName) => {
    const response = await apiClient.patch("/api/v1/settings/profile", {
      full_name: fullName,
    });
    return response.data;
  },
};

export default settingsApi;
