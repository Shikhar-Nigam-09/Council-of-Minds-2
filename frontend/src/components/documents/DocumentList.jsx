/* eslint-disable react/prop-types */
import { useState, useMemo } from "react";
import { Link } from "react-router-dom";

export default function DocumentList({
  documents,
  isLoading,
  onDelete,
  onRename,
  onRetry,
  isDeleting,
  isRenaming,
  isRetrying,
}) {
  const [editingId, setEditingId] = useState(null);
  const [newFilename, setNewFilename] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "uploaded":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            Uploaded
          </span>
        );
      case "processing":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-spin" />
            Processing
          </span>
        );
      case "ready":
      case "indexed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Indexed in FAISS
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            Failed
          </span>
        );
      case "deletion_failed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse" />
            Deletion Failed
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-slate-800 text-slate-300">
            {status}
          </span>
        );
    }
  };

  const handleStartRename = (doc) => {
    setEditingId(doc.id);
    setNewFilename(doc.original_filename);
  };

  const handleSaveRename = async (id) => {
    if (!newFilename.trim()) return;
    await onRename({ id, newFilename: newFilename.trim() });
    setEditingId(null);
  };

  const filteredDocuments = useMemo(() => {
    if (!documents) return [];
    return documents.filter((doc) => {
      const matchesSearch =
        doc.original_filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.id?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus =
        statusFilter === "all" ||
        doc.status === statusFilter ||
        (statusFilter === "indexed" && doc.status === "ready");
      return matchesSearch && matchesStatus;
    });
  }, [documents, searchQuery, statusFilter]);

  if (isLoading) {
    return (
      <div className="w-full backdrop-blur-xl bg-slate-900/60 border border-slate-800/80 rounded-3xl p-12 text-center text-slate-400 flex flex-col items-center justify-center space-y-4">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium">
          Loading your document repository...
        </span>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="w-full backdrop-blur-xl bg-slate-900/40 border border-slate-800/80 rounded-3xl p-12 text-center text-slate-400 space-y-3">
        <div className="text-4xl">📂</div>
        <h4 className="text-base font-semibold text-slate-300">
          No Documents Found
        </h4>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Upload your first PDF, TXT, or Markdown document using the dropzone
          above to begin encapsulating knowledge for the Council of Minds.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full backdrop-blur-xl bg-slate-900/60 border border-slate-800/80 rounded-3xl overflow-hidden shadow-2xl shadow-black/50 space-y-0">
      {/* Table Header & Filter Bar */}
      <div className="p-4 sm:px-6 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <span>Document Repository</span>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[11px] font-mono text-indigo-400 font-bold">
              {filteredDocuments.length} / {documents.length}
            </span>
          </h3>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500 text-xs">
              🔍
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by filename or ID..."
              className="w-full pl-8 pr-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-xs text-slate-500 hover:text-slate-300"
              >
                ✕
              </button>
            )}
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-xl text-xs text-slate-300 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="indexed">Indexed in FAISS</option>
            <option value="processing">Processing</option>
            <option value="uploaded">Uploaded (Pending)</option>
            <option value="failed">Failed Ingestion</option>
          </select>
        </div>
      </div>

      {/* Mobile Stacked Card List (< md) */}
      <div className="md:hidden divide-y divide-slate-800/80 min-w-0">
        {filteredDocuments.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500 italic p-4">
            No documents match your current filter criteria.
          </div>
        ) : (
          filteredDocuments.map((doc) => (
            <div key={doc.id} className="p-4 bg-slate-900/40 space-y-3.5 min-w-0 break-words">
              {/* Header: Filename & Status */}
              <div className="flex items-start justify-between gap-2 min-w-0">
                <div className="min-w-0 flex-1">
                  {editingId === doc.id ? (
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <input
                        type="text"
                        value={newFilename}
                        onChange={(e) => setNewFilename(e.target.value)}
                        className="px-2.5 py-1 bg-slate-950 border border-indigo-500 rounded-lg text-xs text-white focus:outline-none flex-1 min-w-[120px]"
                        autoFocus
                      />
                      <button
                        onClick={() => handleSaveRename(doc.id)}
                        disabled={isRenaming}
                        className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 rounded text-xs font-semibold min-h-[32px]"
                      >
                        ✓
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-2.5 py-1 bg-slate-800 text-slate-400 hover:bg-slate-700 rounded text-xs min-h-[32px]"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2 min-w-0">
                        <Link
                          to={`/documents/${doc.id}`}
                          className="font-bold text-slate-200 hover:text-indigo-400 transition-colors truncate block min-w-0 text-sm"
                          title={doc.original_filename}
                        >
                          {doc.original_filename}
                        </Link>
                        <button
                          onClick={() => handleStartRename(doc)}
                          className="text-slate-500 hover:text-indigo-400 transition-opacity text-xs flex-shrink-0 min-h-[28px] px-1"
                          title="Rename document"
                        >
                          ✎
                        </button>
                      </div>
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-[11px] font-mono text-indigo-400 hover:text-indigo-300"
                      >
                        <span>🔍 Inspect Chunks & Detail View →</span>
                      </Link>
                    </div>
                  )}
                </div>
                <div className="flex-shrink-0">
                  {getStatusBadge(doc.status)}
                </div>
              </div>

              {/* Error Callout */}
              {doc.processing_error && (
                <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-[11px] text-rose-300 break-words font-mono">
                  ⚠️ {doc.processing_error}
                </div>
              )}

              {/* Metadata Grid */}
              <div className="grid grid-cols-3 gap-2 text-xs font-mono text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/60">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-sans font-semibold">Type</span>
                  <span>{doc.file_type.replace("application/", "").replace("text/", "").toUpperCase()}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-sans font-semibold">Size</span>
                  <span>{formatBytes(doc.file_size_bytes)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-sans font-semibold">Uploaded</span>
                  <span className="truncate block">{formatDate(doc.created_at)}</span>
                </div>
              </div>

              {/* Actions Row */}
              <div className="flex items-center gap-2 pt-1 flex-wrap">
                {(doc.status === "failed" ||
                  doc.status === "deletion_failed" ||
                  doc.status === "processing" ||
                  doc.status === "uploaded") && (
                  <button
                    onClick={() => onRetry && onRetry(doc.id)}
                    disabled={isRetrying}
                    className="flex-1 min-w-[90px] inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 text-xs font-semibold transition-all disabled:opacity-50 min-h-[36px]"
                  >
                    <span>↻</span> Retry
                  </button>
                )}
                <a
                  href={doc.cloudinary_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 min-w-[90px] inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all min-h-[36px]"
                >
                  <span>👁</span> View
                </a>
                <button
                  onClick={() => {
                    if (
                      window.confirm(
                        `Are you sure you want to delete '${doc.original_filename}'?`,
                      )
                    ) {
                      onDelete(doc.id);
                    }
                  }}
                  disabled={isDeleting}
                  className="flex-1 min-w-[90px] inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-semibold transition-all disabled:opacity-50 min-h-[36px]"
                >
                  <span>{isDeleting ? "⏳" : "🗑"}</span>{" "}
                  {isDeleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Desktop Table View (>= md) */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800/60 text-[11px] font-semibold uppercase tracking-wider text-slate-400 bg-slate-950/20">
              <th className="py-3.5 px-6">Filename & Inspection</th>
              <th className="py-3.5 px-6">Type</th>
              <th className="py-3.5 px-6">Size</th>
              <th className="py-3.5 px-6">Status</th>
              <th className="py-3.5 px-6">Uploaded</th>
              <th className="py-3.5 px-6 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-sm text-slate-300">
            {filteredDocuments.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-8 text-center text-xs text-slate-500 italic">
                  No documents match your current filter criteria.
                </td>
              </tr>
            ) : (
              filteredDocuments.map((doc) => (
                <tr
                  key={doc.id}
                  className="hover:bg-slate-800/30 transition-colors group"
                >
                  {/* Filename Column with Rename & Link to Detail */}
                  <td className="py-4 px-6 font-medium text-slate-200">
                    {editingId === doc.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={newFilename}
                          onChange={(e) => setNewFilename(e.target.value)}
                          className="px-2.5 py-1 bg-slate-950 border border-indigo-500 rounded-lg text-xs text-white focus:outline-none w-48"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveRename(doc.id)}
                          disabled={isRenaming}
                          className="px-2 py-1 bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 rounded text-xs font-semibold"
                        >
                          ✓
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-2 py-1 bg-slate-800 text-slate-400 hover:bg-slate-700 rounded text-xs"
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/documents/${doc.id}`}
                            className="truncate max-w-xs font-bold text-slate-200 hover:text-indigo-400 transition-colors"
                            title={doc.original_filename}
                          >
                            {doc.original_filename}
                          </Link>
                          <button
                            onClick={() => handleStartRename(doc)}
                            className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-indigo-400 transition-opacity text-xs"
                            title="Rename document"
                          >
                            ✎
                          </button>
                        </div>
                        <Link
                          to={`/documents/${doc.id}`}
                          className="inline-flex items-center gap-1 text-[11px] font-mono text-indigo-400 hover:text-indigo-300"
                        >
                          <span>🔍 Inspect Chunks & Detail View →</span>
                        </Link>
                      </div>
                    )}
                  </td>

                  {/* Type Column */}
                  <td className="py-4 px-6 font-mono text-xs text-slate-400">
                    {doc.file_type
                      .replace("application/", "")
                      .replace("text/", "")
                      .toUpperCase()}
                  </td>

                  {/* Size Column */}
                  <td className="py-4 px-6 font-mono text-xs text-slate-400">
                    {formatBytes(doc.file_size_bytes)}
                  </td>

                  {/* Status Column */}
                  <td className="py-4 px-6">
                    {getStatusBadge(doc.status)}
                    {doc.processing_error && (
                      <div
                        className="text-[10px] text-rose-400 mt-1 max-w-xs truncate"
                        title={doc.processing_error}
                      >
                        {doc.processing_error}
                      </div>
                    )}
                  </td>

                  {/* Date Column */}
                  <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                    {formatDate(doc.created_at)}
                  </td>

                  {/* Actions Column */}
                  <td className="py-4 px-6 text-right space-x-2">
                    {(doc.status === "failed" ||
                      doc.status === "deletion_failed" ||
                      doc.status === "processing" ||
                      doc.status === "uploaded") && (
                      <button
                        onClick={() => onRetry && onRetry(doc.id)}
                        disabled={isRetrying}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 text-xs font-semibold transition-all disabled:opacity-50"
                        title="Retry processing or deletion"
                      >
                        <span>↻</span> Retry
                      </button>
                    )}
                    <a
                      href={doc.cloudinary_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all"
                      title="View file in Cloudinary"
                    >
                      <span>👁</span> View
                    </a>
                    <button
                      onClick={() => {
                        if (
                          window.confirm(
                            `Are you sure you want to delete '${doc.original_filename}'?`,
                          )
                        ) {
                          onDelete(doc.id);
                        }
                      }}
                      disabled={isDeleting}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-semibold transition-all disabled:opacity-50"
                    >
                      <span>{isDeleting ? "⏳" : "🗑"}</span>{" "}
                      {isDeleting ? "Deleting..." : "Delete"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
