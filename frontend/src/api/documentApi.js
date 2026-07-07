import apiClient from "./client";

export const documentApi = {
  uploadDocument: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/api/v1/documents", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
    return response.data;
  },

  listDocuments: async () => {
    const response = await apiClient.get("/api/v1/documents");
    return response.data;
  },

  getDocument: async (id) => {
    const response = await apiClient.get(`/api/v1/documents/${id}`);
    return response.data;
  },

  renameDocument: async ({ id, newFilename }) => {
    const response = await apiClient.patch(`/api/v1/documents/${id}`, {
      new_filename: newFilename,
    });
    return response.data;
  },

  retryDocument: async (id) => {
    const response = await apiClient.post(`/api/v1/documents/${id}/retry`);
    return response.data;
  },

  deleteDocument: async (id) => {
    const response = await apiClient.delete(`/api/v1/documents/${id}`);
    return response.data;
  },

  getDocumentChunks: async ({ id, page = 1, pageSize = 20 }) => {
    const response = await apiClient.get(`/api/v1/documents/${id}/chunks`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};
