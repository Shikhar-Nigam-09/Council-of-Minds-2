import { create } from "zustand";

/**
 * Placeholder Zustand store for global application state.
 */
export const useAppStore = create((set) => ({
  version: "0.1.0",
  setVersion: (version) => set({ version }),
}));

export default useAppStore;
