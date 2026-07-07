import { useState } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";

export default function PasswordChangeForm({ onChangePassword, isChanging }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all password fields.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters long.");
      return;
    }

    if (window.confirm("Changing your password will immediately log you out of all active sessions across all devices. Proceed?")) {
      try {
        await onChangePassword({
          old_password: oldPassword,
          new_password: newPassword,
        });
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to change password. Check your current password.");
      }
    }
  };

  return (
    <Card className="p-4 sm:p-6 md:p-8 space-y-6 border-slate-200/80 dark:border-slate-800/80 min-w-0 break-words">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-4 min-w-0">
        <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
          <span>🔒 Security & Authentication</span>
          <Badge variant="rose" className="text-[10px] uppercase">
            Token Invalidation
          </Badge>
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Update your password and manage active session security tokens.
        </p>
      </div>

      <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-200 text-xs space-y-1 min-w-0 break-words">
        <div className="font-bold flex items-center gap-1.5">
          <span>⚠️ Important Security Notice</span>
        </div>
        <p className="leading-relaxed opacity-90">
          The Council of Minds platform uses strict JWT token versioning. Changing your password will increment your account's token version in PostgreSQL, immediately invalidating all existing access and refresh tokens across all devices. You will be redirected to log in again.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 max-w-xl min-w-0">
        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-semibold break-words">
            {error}
          </div>
        )}

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Current Password
          </label>
          <input
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            placeholder="Enter current password..."
            className="w-full px-3.5 py-2.5 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[40px]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            New Password
          </label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password (min. 8 characters)..."
            className="w-full px-3.5 py-2.5 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[40px]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Confirm New Password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password..."
            className="w-full px-3.5 py-2.5 text-base sm:text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[40px]"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <Button
            type="submit"
            variant="primary"
            disabled={isChanging || !oldPassword || !newPassword || !confirmPassword}
            className="px-6 shadow-md shadow-rose-500/10 bg-rose-600 hover:bg-rose-700 text-white border-none w-full sm:w-auto justify-center min-h-[40px]"
          >
            <span>{isChanging ? "Changing Password..." : "Change Password & Log Out"}</span>
          </Button>
        </div>
      </form>
    </Card>
  );
}
