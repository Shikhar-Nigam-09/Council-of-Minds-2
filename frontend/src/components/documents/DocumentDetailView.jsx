import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";

const STATUS_MAP = {
  uploaded: { label: "Uploaded (Pending)", variant: "blue", dot: "pulse" },
  processing: { label: "Ingesting to RAG...", variant: "indigo", dot: "pulse" },
  indexed: { label: "Indexed in FAISS", variant: "emerald", dot: "success" },
  failed: { label: "Ingestion Failed", variant: "rose", dot: "error" },
  deletion_failed: { label: "Deletion Failed", variant: "rose", dot: "error" },
};

export default function DocumentDetailView({ document, onRetry, isRetrying, onDelete, isDeleting }) {
  if (!document) return null;

  const statusInfo = STATUS_MAP[document.status] || {
    label: document.status,
    variant: "slate",
  };

  const fileSizeKB = (document.file_size_bytes / 1024).toFixed(1);
  const createdDate = new Date(document.created_at).toLocaleString();

  const handleRetry = () => {
    onRetry(document.id);
  };

  const handleDelete = () => {
    if (
      window.confirm(
        `Delete "${document.original_filename}"? This will permanently remove the file from Cloudinary, delete all text chunks from PostgreSQL, and purge vector embeddings from your FAISS index.`
      )
    ) {
      onDelete(document.id);
    }
  };

  return (
    <Card className="p-4 sm:p-6 md:p-8 space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4 min-w-0">
        <div className="space-y-1 min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <Badge variant={statusInfo.variant} dot={statusInfo.dot} className="px-2.5 py-0.5 text-xs font-bold">
              {statusInfo.label}
            </Badge>
            <span className="text-xs font-mono uppercase text-slate-400 dark:text-slate-500">
              Type: {document.file_type}
            </span>
          </div>
          <h2 className="text-lg sm:text-xl md:text-2xl font-extrabold text-slate-900 dark:text-white break-words overflow-wrap-anywhere">
            {document.original_filename}
          </h2>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 flex-wrap w-full sm:w-auto">
          {(document.status === "failed" ||
            document.status === "deletion_failed" ||
            document.status === "uploaded" ||
            document.status === "processing") && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRetry}
              disabled={isRetrying}
              className="text-xs font-semibold shadow-sm flex-1 sm:flex-initial min-h-[36px] justify-center"
            >
              <span>{isRetrying ? "Retrying..." : "🔄 Retry Processing"}</span>
            </Button>
          )}

          <Button
            variant="secondary"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-xs font-semibold text-rose-600 hover:text-white hover:bg-rose-600 border-rose-200 dark:border-rose-900/50 flex-1 sm:flex-initial min-h-[36px] justify-center"
          >
            <span>{isDeleting ? "Deleting..." : "🗑️ Delete Document"}</span>
          </Button>
        </div>
      </div>

      {/* Error Callout */}
      {document.processing_error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-800 dark:text-rose-200 text-xs space-y-1.5">
          <div className="font-bold flex items-center gap-1.5 text-sm">
            <span>⚠️ Ingestion / Processing Error</span>
          </div>
          <p className="font-mono leading-relaxed bg-rose-500/10 p-2.5 rounded-xl border border-rose-500/10">
            {document.processing_error}
          </p>
          <p className="text-[11px] opacity-80 pt-1">
            Click "Retry Processing" above to re-queue this document for background embedding generation.
          </p>
        </div>
      )}

      {/* Metadata Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            File Size
          </span>
          <span className="text-sm font-mono font-bold text-slate-800 dark:text-slate-200">
            {fileSizeKB} KB
          </span>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Upload Date
          </span>
          <span className="text-sm font-mono font-bold text-slate-800 dark:text-slate-200">
            {createdDate}
          </span>
        </div>

        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60 sm:col-span-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Cloudinary Asset ID
          </span>
          <span className="text-xs font-mono text-slate-600 dark:text-slate-400 break-all">
            {document.cloudinary_public_id}
          </span>
        </div>
      </div>

      {/* FAISS Aware Deletion Notice */}
      <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-950 dark:text-indigo-200 text-xs space-y-1">
        <div className="font-bold flex items-center gap-1.5">
          <span>🧠 FAISS-Aware Storage Architecture</span>
        </div>
        <p className="leading-relaxed opacity-90">
          This document is linked directly to your user-scoped FAISS vector index. When deleted or reprocessed, our backend workers atomically purge vector embeddings from FAISS, delete text chunks from PostgreSQL, and remove raw assets from Cloudinary storage to prevent ghost citations.
        </p>
      </div>
    </Card>
  );
}
