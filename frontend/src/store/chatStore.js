import { create } from "zustand";

/**
 * Zustand store for temporary UI state and interaction state in Chat (Phase 8).
 * Per Requirement 3: Server/persisted chat history is managed exclusively in TanStack Query.
 */
export const useChatStore = create((set) => ({
  // Temporary UI states
  pendingQuestion: null, // Holds question string while Council is deliberating
  failedQuestion: null, // Holds { question, chat_id, error } if submission fails
  expandedPanels: {}, // Record<messageId, Record<panelKey, boolean>>

  startDeliberation: (question) =>
    set({ pendingQuestion: question, failedQuestion: null }),

  stopDeliberation: () => set({ pendingQuestion: null }),

  setFailedQuestion: (data) =>
    set({ failedQuestion: data, pendingQuestion: null }),

  clearFailedQuestion: () => set({ failedQuestion: null }),

  togglePanel: (messageId, panelKey) =>
    set((state) => {
      const currentMsgPanels = state.expandedPanels[messageId] || {
        breakdown: false,
        agents: false,
        challenger: false,
        evidence: false,
      };
      return {
        expandedPanels: {
          ...state.expandedPanels,
          [messageId]: {
            ...currentMsgPanels,
            [panelKey]: !currentMsgPanels[panelKey],
          },
        },
      };
    }),

  resetUi: () =>
    set({
      pendingQuestion: null,
      failedQuestion: null,
      expandedPanels: {},
    }),
}));

export default useChatStore;
