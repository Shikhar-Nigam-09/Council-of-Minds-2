import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

export default function ProfileForm({ initialFullName, email, onSave, isSaving }) {
  const [fullName, setFullName] = useState(initialFullName || "");
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setFullName(initialFullName || "");
    setHasChanges(false);
  }, [initialFullName]);

  const handleChange = (val) => {
    setFullName(val);
    setHasChanges(val !== (initialFullName || ""));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSave(fullName);
    setHasChanges(false);
  };

  return (
    <Card className="p-4 sm:p-6 md:p-8 space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-4 min-w-0">
        <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span>👤 Profile Information</span>
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Update your public display name and view account identification details.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Email Address (Read-Only)
          </label>
          <input
            type="email"
            value={email || ""}
            disabled
            className="w-full px-3.5 py-2.5 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 cursor-not-allowed font-mono min-h-[40px]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Display Name
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => handleChange(e.target.value)}
            placeholder="Enter your full name..."
            className="w-full px-3.5 py-2.5 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[40px]"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <Button
            type="submit"
            variant="primary"
            disabled={!hasChanges || isSaving}
            className="px-6 shadow-md shadow-indigo-500/10 w-full sm:w-auto justify-center min-h-[40px]"
          >
            <span>{isSaving ? "Saving..." : "Update Profile"}</span>
          </Button>
        </div>
      </form>
    </Card>
  );
}
