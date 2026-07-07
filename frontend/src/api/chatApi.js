import apiClient from "./client";

export const chatApi = {
  sendMessage: async ({ question, chat_id, agent_weights }) => {
    const payload = { question };
    if (chat_id) payload.chat_id = chat_id;
    if (agent_weights) payload.agent_weights = agent_weights;
    const response = await apiClient.post("/api/v1/chats/messages", payload);
    return response.data;
  },

  listChats: async () => {
    const response = await apiClient.get("/api/v1/chats");
    return response.data;
  },

  getChat: async (chatId) => {
    const response = await apiClient.get(`/api/v1/chats/${chatId}`);
    return response.data;
  },

  deleteChat: async (chatId) => {
    const response = await apiClient.delete(`/api/v1/chats/${chatId}`);
    return response.data;
  },
};
