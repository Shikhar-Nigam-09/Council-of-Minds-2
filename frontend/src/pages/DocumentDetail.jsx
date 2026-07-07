import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useDocumentDetail, useDocumentChunks, useDocuments } from "../hooks/useDocuments";
import DocumentDetailView from "../components/documents/DocumentDetailView";
import ChunkPreview from "../components/documents/ChunkPreview";
import Button from "../components/ui/Button";

export default function DocumentDetail() {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const { document, isLoading: isLoadingDoc, error: docError } = useDocumentDetail(documentId);
  const { data: chunkData, isLoading: isLoadingChunks } = useDocumentChunks(documentId, page, pageSize);
  const { retryDocument, isRetrying, deleteDocument, isDeleting } = useDocuments();

  const handleRetry = async (id) => {
    try {
      await retryDocument(id);
    } catch (err) {
      alert("Failed to retry document processing: " + (err?.message || "Unknown error"));
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id);
      navigate("/documents");
    } catch (err) {
      alert("Failed to delete document: " + (err?.message || "Unknown error"));
    }
  };

  if (isLoadingDoc) {
    return (
      <div className="max-w-5xl mx-auto py-20 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
          Loading document metadata & embeddings...
        </p>
      </div>
    );
  }

  if (docError || !document) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="p-8 rounded-3xl bg-rose-500/10 border border-rose-500/20 text-center space-y-4">
          <div className="text-4xl">⚠️</div>
          <h2 className="text-lg font-bold text-rose-600 dark:text-rose-400">
            Document Not Found or Access Denied
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
            {docError?.message || "The requested document could not be loaded from PostgreSQL or FAISS index."}
          </p>
          <div className="pt-2">
            <Link to="/documents">
              <Button variant="secondary" size="sm">
                <span>← Back to Document Repository</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 py-6 sm:py-8 px-2 sm:px-4 min-w-0 break-words">
      {/* Back Navigation & Breadcrumbs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 min-w-0">
        <Link
          to="/documents"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors bg-slate-100 dark:bg-slate-900/80 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 min-h-[36px]"
        >
          <span>← Back to Document Repository</span>
        </Link>
        <span className="text-xs font-mono text-slate-400 dark:text-slate-500 truncate max-w-full">
          ID: {document.id}
        </span>
      </div>

      {/* Document Metadata Overview */}
      <DocumentDetailView
        document={document}
        onRetry={handleRetry}
        isRetrying={isRetrying}
        onDelete={handleDelete}
        isDeleting={isDeleting}
      />

      {/* Paginated Chunks Inspection */}
      <ChunkPreview
        data={chunkData}
        isLoading={isLoadingChunks}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
      />
    </div>
  );
}
