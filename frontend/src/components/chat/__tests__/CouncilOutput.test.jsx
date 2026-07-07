import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/utils';
import AssistantMessage from '../AssistantMessage';
import ChallengerPanel from '../ChallengerPanel';

const mockUseChatStore = vi.fn();

vi.mock('../../../store/chatStore', () => ({
  useChatStore: () => mockUseChatStore(),
}));

describe('Council Output Rendering Regression Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseChatStore.mockReturnValue({
      expandedPanels: {
        'msg-test': {
          breakdown: false,
          agents: false,
          challenger: true,
          evidence: false,
        },
      },
      togglePanel: vi.fn(),
    });
  });

  it('renders the aggregated final answer in AssistantMessage without depending on a status field', () => {
    const mockMessage = {
      id: 'msg-test',
      role: 'assistant',
      content: 'This is the comprehensive synthesized answer from all five reasoning personas.',
      confidence_score: 0.92,
      agent_responses: [],
      evidence: [],
    };

    renderWithProviders(<AssistantMessage message={mockMessage} />);
    expect(screen.getByText('This is the comprehensive synthesized answer from all five reasoning personas.')).toBeInTheDocument();
  });

  it('renders the Challenger critique with critique summary and structured lists', () => {
    const mockChallengerResponse = {
      agent_name: 'challenger',
      answer: 'The aggregated answer is logically sound but assumes infinite database scaling.',
      key_points: {
        weaknesses: ['Assumes zero network latency between database nodes.'],
        unsupported_claims: ['Claiming 100% data consistency is not backed by the evidence.'],
        missing_considerations: ['Need to evaluate failover recovery time.'],
      },
      self_reported_confidence: 0.0,
      latency_ms: 1540,
    };

    renderWithProviders(<ChallengerPanel challengerResponse={mockChallengerResponse} />);
    
    // Check critique summary
    expect(screen.getByText('The aggregated answer is logically sound but assumes infinite database scaling.')).toBeInTheDocument();
    
    // Check weaknesses
    expect(screen.getByText('⚠️ Logical & Empirical Weaknesses:')).toBeInTheDocument();
    expect(screen.getByText('Assumes zero network latency between database nodes.')).toBeInTheDocument();
    
    // Check unsupported claims
    expect(screen.getByText('🚫 Unsupported Claims:')).toBeInTheDocument();
    expect(screen.getByText('Claiming 100% data consistency is not backed by the evidence.')).toBeInTheDocument();
    
    // Check missing considerations
    expect(screen.getByText('🔍 Missing Considerations:')).toBeInTheDocument();
    expect(screen.getByText('Need to evaluate failover recovery time.')).toBeInTheDocument();
    
    // Check latency display
    expect(screen.getByText(/1540ms/)).toBeInTheDocument();
  });

  it('renders ChallengerPanel when embedded inside AssistantMessage when expanded', () => {
    const mockMessage = {
      id: 'msg-test',
      role: 'assistant',
      content: 'Synthesized council answer.',
      confidence_score: 0.88,
      agent_responses: [
        {
          agent_name: 'challenger',
          answer: 'Red-team critique summary inside AssistantMessage.',
          key_points: {
            weaknesses: ['Weakness A'],
            unsupported_claims: ['Unsupported B'],
            missing_considerations: ['Missing C'],
          },
          self_reported_confidence: 0.0,
          latency_ms: 1200,
        },
      ],
      evidence: [],
    };

    renderWithProviders(<AssistantMessage message={mockMessage} />);
    expect(screen.getByText('Synthesized council answer.')).toBeInTheDocument();
    expect(screen.getByText('Red-team critique summary inside AssistantMessage.')).toBeInTheDocument();
    expect(screen.getByText('Weakness A')).toBeInTheDocument();
    expect(screen.getByText('Unsupported B')).toBeInTheDocument();
    expect(screen.getByText('Missing C')).toBeInTheDocument();
  });
});
