import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useUiStore = create(
  persist(
    (set, get) => ({
      theme: "dark",
      sidebarCollapsed: false,
      mobileDrawerOpen: false,
      toasts: [],

      toggleMobileDrawer: () =>
        set((state) => ({ mobileDrawerOpen: !state.mobileDrawerOpen })),
      setMobileDrawerOpen: (open) => set({ mobileDrawerOpen: open }),
      closeMobileDrawer: () => set({ mobileDrawerOpen: false }),

      setTheme: (theme) => {
        set({ theme });
        if (typeof document !== "undefined") {
          const root = document.documentElement;
          if (theme === "dark") {
            root.classList.add("dark");
          } else {
            root.classList.remove("dark");
          }
        }
      },

      toggleTheme: () => {
        const current = get().theme;
        const next = current === "dark" ? "light" : "dark";
        get().setTheme(next);
      },

      initTheme: () => {
        const current = get().theme;
        if (typeof document !== "undefined") {
          const root = document.documentElement;
          if (current === "dark") {
            root.classList.add("dark");
          } else {
            root.classList.remove("dark");
          }
        }
      },

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      addToast: ({ title, message, type = "info", duration = 4000 }) => {
        const id =
          Date.now().toString() + Math.random().toString(36).substring(2, 5);
        const toast = { id, title, message, type, duration };
        set((state) => ({ toasts: [...state.toasts, toast] }));
        return id;
      },

      removeToast: (id) =>
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        })),

      clearToasts: () => set({ toasts: [] }),
    }),
    {
      name: "com_ui_storage",
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && typeof document !== "undefined") {
          const root = document.documentElement;
          if (state.theme === "dark") {
            root.classList.add("dark");
          } else {
            root.classList.remove("dark");
          }
        }
      },
    },
  ),
);

// Register globally for non-component usage (like apiErrorHandler)
if (typeof window !== "undefined") {
  window.__COM_UI_STORE__ = useUiStore;
  // Initialize class immediately
  const stored = localStorage.getItem("com_ui_storage");
  let initialTheme = "dark";
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      if (parsed?.state?.theme) {
        initialTheme = parsed.state.theme;
      }
    } catch {
      // ignore
    }
  }
  if (initialTheme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

export default useUiStore;
