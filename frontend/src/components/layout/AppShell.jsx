import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import Toast from "../ui/Toast";
import useUiStore from "../../store/uiStore";

export default function AppShell() {
  const { mobileDrawerOpen, closeMobileDrawer } = useUiStore();

  useEffect(() => {
    if (mobileDrawerOpen && typeof document !== "undefined") {
      document.body.style.overflow = "hidden";
    } else if (typeof document !== "undefined") {
      document.body.style.overflow = "";
    }
    return () => {
      if (typeof document !== "undefined") {
        document.body.style.overflow = "";
      }
    };
  }, [mobileDrawerOpen]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex overflow-hidden relative transition-colors duration-300">
      {/* Background Ambient Lighting Effects */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-600/15 rounded-full blur-3xl pointer-events-none animate-pulse z-0" />
      <div className="absolute bottom-10 left-1/3 w-96 h-96 bg-purple-500/10 dark:bg-purple-600/15 rounded-full blur-3xl pointer-events-none animate-pulse delay-700 z-0" />

      {/* Mobile Drawer Backdrop Overlay */}
      {mobileDrawerOpen && (
        <div
          onClick={closeMobileDrawer}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
          aria-hidden="true"
        />
      )}

      {/* Persistent Sidebar Navigation */}
      <Sidebar />

      {/* Main Column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
        {/* Top Header */}
        <Topbar />

        {/* Scrollable Page Content Area */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 sm:p-6 md:p-8 max-w-7xl mx-auto w-full min-w-0">
          <Outlet />
        </main>
      </div>

      {/* Global Toast Notification Container */}
      <Toast />
    </div>
  );
}
