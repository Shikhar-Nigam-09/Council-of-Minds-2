import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../test/utils';
import Chat from '../Chat';

const mockSendMessage = vi.fn();
const mockUseChat = vi.fn();
const mockUseDocuments = vi.fn();
const mockUseChatStore = vi.fn();

vi.mock('../../hooks/useChat', () => ({
  useChat: (id) => mockUseChat(id),
}));

vi.mock('../../hooks/useDocuments', () => ({
  useDocuments: () => mockUseDocuments(),
}));

vi.mock('../../store/chatStore', () => ({
  useChatStore: () => mockUseChatStore(),
}));

describe('Chat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
    });
    mockUseChatStore.mockReturnValue({
      pendingQuestion: null,
      failedQuestion: null,
      clearFailedQuestion: vi.fn(),
      expandedPanels: {},
      togglePanel: vi.fn(),
    });
  });

  it('renders client-side session header when no chatId is in URL', () => {
    mockUseChat.mockReturnValue({
      chat: null,
      isLoading: false,
      sendMessage: mockSendMessage,
      isSending: false,
    });

    renderWithProviders(<Chat />);
    expect(screen.getByText('New Debate Session')).toBeInTheDocument();
    expect(screen.getByText(/client-side session/i)).toBeInTheDocument();
  });

  it('renders messages when chat session is loaded', () => {
    mockUseChat.mockReturnValue({
      chat: {
        id: 'chat-123',
        title: 'Quantum Computing Debate',
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'What is qubits?',
            created_at: '2026-07-05T12:00:00Z',
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: 'A qubit is a quantum bit.',
            created_at: '2026-07-05T12:00:05Z',
            confidence_breakdown: {
              retrieval_quality: 0.9,
              evidence_coverage: 0.85,
              agent_agreement: 0.95,
              overall_confidence: 0.9,
            },
          },
        ],
      },
      isLoading: false,
      sendMessage: mockSendMessage,
      isSending: false,
    });

    renderWithProviders(<Chat />);
    expect(screen.getByText('What is qubits?')).toBeInTheDocument();
    expect(screen.getByText('A qubit is a quantum bit.')).toBeInTheDocument();
  });
});
