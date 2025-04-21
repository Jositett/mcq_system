import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import BulkStudentUpload from '../components/BulkStudentUpload';
import axios from 'axios';

jest.mock('axios');

const mockToken = 'testtoken';

describe('BulkStudentUpload', () => {
  beforeEach(() => {
    axios.post.mockClear();
  });

  it('renders upload instructions and buttons', () => {
    render(<BulkStudentUpload token={mockToken} />);
    expect(screen.getByText(/Download the/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Choose CSV/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload/i })).toBeInTheDocument();
  });

  it('shows preview after CSV file is selected', async () => {
    render(<BulkStudentUpload token={mockToken} />);
    const file = new File([
      'full_name,email,roll_number,dob,batch_name\nJohn Doe,john@example.com,123,2000-01-01,Batch A',
    ], 'students.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/choose csv/i) || screen.getByRole('button', { name: /Choose CSV/i }).previousSibling;
    // Simulate file input (using fireEvent.change with files)
    fireEvent.change(input, { target: { files: [file] } });
    await waitFor(() => expect(screen.getByText(/Preview/i)).toBeInTheDocument());
    expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
  });

  it('handles successful upload', async () => {
    axios.post.mockResolvedValueOnce({ data: { results: [{ full_name: 'John Doe', email: 'john@example.com', batch_name: 'Batch A', success: true, error: null }] } });
    render(<BulkStudentUpload token={mockToken} />);
    // Simulate preview state
    fireEvent.click(screen.getByRole('button', { name: /Upload/i }));
    await waitFor(() => expect(axios.post).toHaveBeenCalled());
  });

  it('handles upload error', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Bulk upload failed' } } });
    render(<BulkStudentUpload token={mockToken} />);
    fireEvent.click(screen.getByRole('button', { name: /Upload/i }));
    await waitFor(() => expect(screen.getByText(/Bulk upload failed/i)).toBeInTheDocument());
  });
});
