import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../test/utils';
import Login from '../Login';

const mockLogin = vi.fn();
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    isLoggingIn: false,
  }),
}));

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form heading and inputs', () => {
    renderWithProviders(<Login />);
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('displays registration success banner when registered query param is present', () => {
    renderWithProviders(<Login />, { route: '/login?registered=true' });
    expect(
      screen.getByText(/registration successful! please sign in below\./i)
    ).toBeInTheDocument();
  });

  it('submits email and password when sign in button is clicked', async () => {
    renderWithProviders(<Login />);
    
    const emailInput = screen.getByPlaceholderText('you@example.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    const submitBtn = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecretPass123!' } });
    fireEvent.click(submitBtn);

    expect(mockLogin).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'SecretPass123!',
    });
  });
});
