import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";

export default function ChunkPreview({ data, isLoading, page, pageSize, onPageChange }) {
  const chunks = data?.chunks || [];
  const total = data?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <Card className="p-4 sm:p-6 md:p-8 space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
            <span>🧩 Extracted Vector Chunks</span>
            <Badge variant="indigo" className="text-[10px] font-mono">
              {total} Total Chunks
            </Badge>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Inspect the segmented text chunks and FAISS embedding IDs indexed for contextual retrieval.
          </p>
        </div>

        {totalPages > 1 && (
          <div className="flex items-center gap-2 flex-wrap justify-between sm:justify-end w-full sm:w-auto">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1 || isLoading}
              className="text-xs px-3 min-h-[36px] flex-1 sm:flex-initial justify-center"
            >
              <span>← Prev</span>
            </Button>
            <span className="text-xs font-mono font-bold px-2 text-slate-600 dark:text-slate-300">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages || isLoading}
              className="text-xs px-3 min-h-[36px] flex-1 sm:flex-initial justify-center"
            >
              <span>Next →</span>
            </Button>
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="py-12 text-center space-y-3">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Loading paginated chunks...
          </p>
        </div>
      ) : chunks.length === 0 ? (
        <div className="py-12 text-center space-y-2 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-4">
          <div className="text-3xl">📭</div>
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
            No chunks indexed yet
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            This document may still be processing in the background or failed during embedding generation.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {chunks.map((chunk) => {
            const charCount = chunk.content?.length || 0;
            return (
              <div
                key={chunk.id}
                className="p-3.5 sm:p-4 rounded-2xl bg-slate-50/80 dark:bg-slate-900/50 border border-slate-200/80 dark:border-slate-800/80 space-y-3 transition-all hover:border-indigo-500/40 min-w-0 break-words"
              >
                <div className="flex items-center justify-between gap-3 flex-wrap border-b border-slate-200/60 dark:border-slate-800/60 pb-2.5 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge variant="indigo" className="text-xs font-mono font-bold">
                      Chunk #{chunk.chunk_index}
                    </Badge>
                    <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
                      {charCount} chars
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[11px] font-mono text-slate-500 dark:text-slate-400 min-w-0">
                    <span className="text-slate-400">FAISS ID:</span>
                    <span className="bg-white dark:bg-slate-950 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-800 text-indigo-600 dark:text-indigo-400 font-bold select-all truncate max-w-[150px] sm:max-w-none">
                      {chunk.faiss_vector_id}
                    </span>
                  </div>
                </div>

                <div className="text-xs sm:text-sm font-sans text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto pr-2 font-normal break-words overflow-wrap-anywhere">
                  {chunk.content}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-4 gap-3">
          <span className="text-xs text-slate-500 font-mono text-center sm:text-left">
            Showing chunks {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
          </span>
          <div className="flex items-center gap-2 w-full sm:w-auto justify-center sm:justify-end">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1 || isLoading}
              className="text-xs px-3 min-h-[36px] flex-1 sm:flex-initial justify-center"
            >
              <span>← Prev</span>
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages || isLoading}
              className="text-xs px-3 min-h-[36px] flex-1 sm:flex-initial justify-center"
            >
              <span>Next →</span>
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
