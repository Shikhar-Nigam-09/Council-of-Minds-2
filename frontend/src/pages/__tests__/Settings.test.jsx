import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../test/utils';
import Settings from '../Settings';

const mockUpdateAgentWeights = vi.fn();
const mockUpdateProfile = vi.fn();
const mockChangePassword = vi.fn();

const mockUseSettings = vi.fn();
vi.mock('../../hooks/useSettings', () => ({
  useSettings: () => mockUseSettings(),
}));

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    changePassword: mockChangePassword,
    isChangingPassword: false,
  }),
}));

describe('Settings Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders settings header and tab buttons', () => {
    mockUseSettings.mockReturnValue({
      settings: {
        agent_weights: {
          logical: 0.2,
          rational: 0.2,
          practical: 0.2,
          spiritual: 0.2,
          skeptical: 0.2,
        },
        full_name: 'Test User',
        email: 'test@example.com',
      },
      isLoading: false,
      updateAgentWeights: mockUpdateAgentWeights,
      isUpdatingWeights: false,
      updateProfile: mockUpdateProfile,
      isUpdatingProfile: false,
    });

    renderWithProviders(<Settings />);
    expect(screen.getByText('System & Agent Settings')).toBeInTheDocument();
    expect(screen.getByText(/persona weights/i)).toBeInTheDocument();
    expect(screen.getByText(/profile & account/i)).toBeInTheDocument();
  });

  it('switches to Profile tab when clicked', () => {
    mockUseSettings.mockReturnValue({
      settings: {
        agent_weights: {
          logical: 0.2,
          rational: 0.2,
          practical: 0.2,
          spiritual: 0.2,
          skeptical: 0.2,
        },
        full_name: 'Test User',
        email: 'test@example.com',
      },
      isLoading: false,
      updateAgentWeights: mockUpdateAgentWeights,
      isUpdatingWeights: false,
      updateProfile: mockUpdateProfile,
      isUpdatingProfile: false,
    });

    renderWithProviders(<Settings />);
    
    const profileTabBtn = screen.getByRole('button', { name: /profile & account/i });
    fireEvent.click(profileTabBtn);

    expect(screen.getByText(/display name & id/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
  });
});
