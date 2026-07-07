import { useDocuments } from "../hooks/useDocuments";
import UploadDropzone from "../components/documents/UploadDropzone";
import DocumentList from "../components/documents/DocumentList";

export default function Documents() {
  const {
    documents,
    isLoading,
    uploadDocument,
    isUploading,
    deleteDocument,
    isDeleting,
    renameDocument,
    isRenaming,
    retryDocument,
    isRetrying,
  } = useDocuments();

  return (
    <div className="space-y-8 sm:space-y-10 pb-8 min-w-0 w-full">
      <div className="text-center max-w-3xl mx-auto px-2 min-w-0 break-words">
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-black tracking-tight mb-4 leading-tight text-slate-900 dark:text-white">
          Document Intelligence & <br />
          <span className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            RAG Vector Ingestion Pipeline.
          </span>
        </h1>
        <p className="text-xs sm:text-sm md:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
          Upload PDF, TXT, or Markdown documents. Files are automatically
          extracted, chunked, and vectorized via sentence-transformers into
          per-user FAISS indexes with real-time status polling and recovery.
        </p>
      </div>

      {/* Upload Dropzone */}
      <UploadDropzone onUpload={uploadDocument} isUploading={isUploading} />

      {/* Document Repository Table */}
      <DocumentList
        documents={documents}
        isLoading={isLoading}
        onDelete={deleteDocument}
        onRename={renameDocument}
        onRetry={retryDocument}
        isDeleting={isDeleting}
        isRenaming={isRenaming}
        isRetrying={isRetrying}
      />
    </div>
  );
}
