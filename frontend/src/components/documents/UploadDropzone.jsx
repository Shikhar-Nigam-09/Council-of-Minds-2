/* eslint-disable react/prop-types */
import { useState, useRef } from "react";

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export default function UploadDropzone({ onUpload, isUploading }) {
  const [isDragging, setIsDragging] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const validateAndUpload = async (file) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    setUploadProgress(0);

    if (!file) return;

    // Validate file extension
    const filename = file.name || "";
    const ext = filename.substring(filename.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setErrorMsg(
        `Unsupported file type '${ext}'. Only PDF, TXT, and MD files are allowed.`,
      );
      return;
    }

    // Validate file size
    if (file.size > MAX_SIZE_BYTES) {
      setErrorMsg(
        `File size (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds limit of ${MAX_SIZE_MB} MB.`,
      );
      return;
    }

    try {
      await onUpload({
        file,
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1),
          );
          setUploadProgress(percent);
        },
      });
      setSuccessMsg(`Successfully uploaded '${file.name}' to Cloudinary!`);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail ||
          err.message ||
          "Upload failed. Please try again.",
      );
    } finally {
      setTimeout(() => setUploadProgress(0), 1500);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isUploading) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (isUploading) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await validateAndUpload(files[0]);
    }
  };

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await validateAndUpload(files[0]);
    }
  };

  return (
    <div className="w-full mb-8">
      {/* Alert banners */}
      {errorMsg && (
        <div className="mb-4 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-3">
            <span className="text-lg">✕</span>
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={() => setErrorMsg(null)}
            className="text-rose-400 hover:text-rose-200"
          >
            ✕
          </button>
        </div>
      )}

      {successMsg && (
        <div className="mb-4 p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-3">
            <span className="text-lg">✓</span>
            <span>{successMsg}</span>
          </div>
          <button
            onClick={() => setSuccessMsg(null)}
            className="text-emerald-400 hover:text-emerald-200"
          >
            ✕
          </button>
        </div>
      )}

      {/* Dropzone Container */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={`relative cursor-pointer group rounded-3xl border-2 border-dashed p-6 sm:p-8 text-center transition-all duration-300 backdrop-blur-xl min-w-0 break-words ${
          isDragging
            ? "border-indigo-500 bg-indigo-500/10 scale-[1.01] shadow-2xl shadow-indigo-500/20"
            : isUploading
              ? "border-slate-700 bg-slate-900/40 cursor-wait opacity-80"
              : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/80 shadow-xl shadow-black/40"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
          onChange={handleFileChange}
          disabled={isUploading}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div
            className={`w-14 h-14 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center text-xl sm:text-2xl transition-all duration-300 ${
              isDragging
                ? "bg-indigo-500 text-white scale-110 shadow-lg shadow-indigo-500/50"
                : "bg-gradient-to-br from-indigo-500/20 to-purple-500/20 text-indigo-400 group-hover:scale-105 border border-indigo-500/30"
            }`}
          >
            📄
          </div>

          <div className="min-w-0 max-w-full">
            <h3 className="text-base sm:text-lg font-bold text-slate-100 group-hover:text-white transition-colors break-words">
              {isUploading
                ? "Uploading & Encapsulating Document..."
                : "Drag & Drop Document Here"}
            </h3>
            <p className="text-xs text-slate-400 mt-1 break-words">
              or{" "}
              <span className="text-indigo-400 font-semibold underline">
                browse from your computer
              </span>
            </p>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-2 sm:gap-4 text-[11px] text-slate-500 uppercase tracking-wider font-mono">
            <span>Supported: PDF, TXT, MD</span>
            <span className="hidden sm:inline">•</span>
            <span>Max Size: 10 MB</span>
          </div>
        </div>

        {/* Progress Bar */}
        {isUploading && uploadProgress > 0 && (
          <div className="mt-6 w-full max-w-xs mx-auto">
            <div className="flex justify-between text-xs font-mono text-indigo-300 mb-1">
              <span>Uploading to Cloudinary</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-200 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
