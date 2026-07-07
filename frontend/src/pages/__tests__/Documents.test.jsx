import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../test/utils';
import Documents from '../Documents';

const mockUploadDocument = vi.fn();
const mockDeleteDocument = vi.fn();
const mockRenameDocument = vi.fn();
const mockRetryDocument = vi.fn();

const mockUseDocuments = vi.fn();
vi.mock('../../hooks/useDocuments', () => ({
  useDocuments: () => mockUseDocuments(),
}));

describe('Documents Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders heading and dropzone when document list is empty', () => {
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      uploadDocument: mockUploadDocument,
      isUploading: false,
      deleteDocument: mockDeleteDocument,
      isDeleting: false,
      renameDocument: mockRenameDocument,
      isRenaming: false,
      retryDocument: mockRetryDocument,
      isRetrying: false,
    });

    renderWithProviders(<Documents />);
    expect(screen.getByText(/document intelligence &/i)).toBeInTheDocument();
    expect(screen.getByText(/drag & drop document here/i)).toBeInTheDocument();
  });

  it('renders document item and status badge when populated', () => {
    mockUseDocuments.mockReturnValue({
      documents: [
        {
          id: 'doc-1',
          original_filename: 'architecture_spec.pdf',
          file_type: 'application/pdf',
          status: 'completed',
          file_size_bytes: 2048,
          created_at: '2026-07-05T12:00:00Z',
        },
      ],
      isLoading: false,
      uploadDocument: mockUploadDocument,
      isUploading: false,
      deleteDocument: mockDeleteDocument,
      isDeleting: false,
      renameDocument: mockRenameDocument,
      isRenaming: false,
      retryDocument: mockRetryDocument,
      isRetrying: false,
    });

    renderWithProviders(<Documents />);
    expect(screen.getAllByText('architecture_spec.pdf').length).toBeGreaterThan(0);
    expect(screen.getAllByText('completed').length).toBeGreaterThan(0);
    expect(screen.getAllByText('2 KB').length).toBeGreaterThan(0);
  });
});
