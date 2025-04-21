import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import BulkQuestionUpload from '../components/BulkQuestionUpload';
import axios from 'axios';

jest.mock('axios');

const mockToken = 'testtoken';

describe('BulkQuestionUpload', () => {
  beforeEach(() => {
    axios.post.mockClear();
  });

  it('renders upload instructions and buttons', () => {
    render(<BulkQuestionUpload token={mockToken} />);
    expect(screen.getByText(/Download the/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Choose CSV/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload/i })).toBeInTheDocument();
  });

  it('shows preview after CSV file is selected', async () => {
    render(<BulkQuestionUpload token={mockToken} />);
    const file = new File([
      'test_name,question_text,question_type,options,correct_answer\nMidterm 1,What is 2+2?,mcq,"[4,3,2,1]",4',
    ], 'questions.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/choose csv/i) || screen.getByRole('button', { name: /Choose CSV/i }).previousSibling;
    fireEvent.change(input, { target: { files: [file] } });
    await waitFor(() => expect(screen.getByText(/Preview/i)).toBeInTheDocument());
    expect(screen.getByText(/What is 2\+2/i)).toBeInTheDocument();
  });

  it('handles successful upload', async () => {
    axios.post.mockResolvedValueOnce({ data: { results: [{ question_text: 'What is 2+2?', test_name: 'Midterm 1', success: true, error: null }] } });
    render(<BulkQuestionUpload token={mockToken} />);
    fireEvent.click(screen.getByRole('button', { name: /Upload/i }));
    await waitFor(() => expect(axios.post).toHaveBeenCalled());
  });

  it('handles upload error', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Bulk upload failed' } } });
    render(<BulkQuestionUpload token={mockToken} />);
    fireEvent.click(screen.getByRole('button', { name: /Upload/i }));
    await waitFor(() => expect(screen.getByText(/Bulk upload failed/i)).toBeInTheDocument());
  });
});
