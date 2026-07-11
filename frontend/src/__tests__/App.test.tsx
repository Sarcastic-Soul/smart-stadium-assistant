import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import '../i18n/resources';

describe('App', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the app title', () => {
    render(<App />);
    expect(screen.getByText('Smart Stadium Assistant')).toBeInTheDocument();
  });

  it('renders navigation tabs', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: /AI Assistant/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Stadium Map/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Dashboard/i })).toBeInTheDocument();
  });

  it('shows chat panel by default', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: /AI Assistant/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('switches tabs on click', async () => {
    const user = userEvent.setup();
    render(<App />);
    const mapTab = screen.getByRole('tab', { name: /Stadium Map/i });
    await user.click(mapTab);
    expect(mapTab).toHaveAttribute('aria-selected', 'true');
  });

  it('has a skip-to-content link', () => {
    render(<App />);
    expect(screen.getByText(/Skip to main content/i)).toBeInTheDocument();
  });

  it('has a language selector', () => {
    render(<App />);
    expect(screen.getByLabelText(/Select language/i)).toBeInTheDocument();
  });

  it('renders chat input', () => {
    render(<App />);
    expect(screen.getByLabelText(/Type your message/i)).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<App />);
    expect(screen.getByLabelText(/Send message/i)).toBeInTheDocument();
  });
});
