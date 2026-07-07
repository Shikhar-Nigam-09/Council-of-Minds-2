import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { documentApi } from "../api/documentApi";

export const useDocuments = () => {
  const queryClient = useQueryClient();

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentApi.listDocuments,
    refetchInterval: (queryOrData) => {
      const docs = Array.isArray(queryOrData)
        ? queryOrData
        : queryOrData?.state?.data || queryOrData?.data || [];
      const hasProcessing = docs.some(
        (doc) => doc.status === "processing" || doc.status === "uploaded",
      );
      return hasProcessing ? 3000 : false;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, onUploadProgress }) =>
      documentApi.uploadDocument(file, onUploadProgress),
    onSuccess: (newDoc) => {
      // Optimistic insert into cache
      queryClient.setQueryData(["documents"], (old = []) => [newDoc, ...old]);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => documentApi.deleteDocument(id),
    onMutate: async (deletedId) => {
      await queryClient.cancelQueries({ queryKey: ["documents"] });
      const previousDocs = queryClient.getQueryData(["documents"]);
      queryClient.setQueryData(["documents"], (old = []) =>
        old.filter((doc) => doc.id !== deletedId),
      );
      return { previousDocs };
    },
    onError: (err, deletedId, context) => {
      if (context?.previousDocs) {
        queryClient.setQueryData(["documents"], context.previousDocs);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const renameMutation = useMutation({
    mutationFn: ({ id, newFilename }) =>
      documentApi.renameDocument({ id, newFilename }),
    onSuccess: (updatedDoc) => {
      queryClient.setQueryData(["documents"], (old = []) =>
        old.map((doc) => (doc.id === updatedDoc.id ? updatedDoc : doc)),
      );
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const retryMutation = useMutation({
    mutationFn: (id) => documentApi.retryDocument(id),
    onSuccess: (updatedDoc) => {
      if (updatedDoc.status === "deleted") {
        queryClient.setQueryData(["documents"], (old = []) =>
          old.filter((doc) => doc.id !== updatedDoc.id),
        );
      } else {
        queryClient.setQueryData(["documents"], (old = []) =>
          old.map((doc) => (doc.id === updatedDoc.id ? updatedDoc : doc)),
        );
      }
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  return {
    documents: documentsQuery.data || [],
    isLoading: documentsQuery.isLoading,
    error: documentsQuery.error,
    refetch: documentsQuery.refetch,
    uploadDocument: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    deleteDocument: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
    renameDocument: renameMutation.mutateAsync,
    isRenaming: renameMutation.isPending,
    retryDocument: retryMutation.mutateAsync,
    isRetrying: retryMutation.isPending,
  };
};

export const useDocumentDetail = (id) => {
  const query = useQuery({
    queryKey: ["document", id],
    queryFn: () => documentApi.getDocument(id),
    enabled: Boolean(id),
  });

  return {
    document: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
};

export const useDocumentChunks = (id, page = 1, pageSize = 20) => {
  const query = useQuery({
    queryKey: ["documentChunks", id, page, pageSize],
    queryFn: () => documentApi.getDocumentChunks({ id, page, pageSize }),
    enabled: Boolean(id),
  });

  return {
    data: query.data || { chunks: [], total: 0, page, page_size: pageSize },
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
};
