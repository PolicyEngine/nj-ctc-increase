import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import PolicyOverview from '../components/PolicyOverview';

describe('PolicyOverview', () => {
  it('renders the enacted-law heading', () => {
    render(<PolicyOverview />);
    expect(
      screen.getByText("New Jersey's enacted Child Tax Credit increase"),
    ).toBeInTheDocument();
  });

  it('displays the four summary cards', () => {
    render(<PolicyOverview />);
    expect(screen.getByText('What changed')).toBeInTheDocument();
    expect(screen.getByText('Effective 2026–2028')).toBeInTheDocument();
    expect(screen.getByText('Cost')).toBeInTheDocument();
    expect(screen.getByText('Who benefits')).toBeInTheDocument();
  });

  it('displays the credit amounts table with all five brackets', () => {
    render(<PolicyOverview />);
    expect(
      screen.getByText('Credit amounts per child (tax years 2026–2028)'),
    ).toBeInTheDocument();
    expect(screen.getByText('$30,000 or less')).toBeInTheDocument();
    expect(screen.getByText('$60,001 – $80,000')).toBeInTheDocument();
    expect(screen.getByText('$1,250')).toBeInTheDocument();
    expect(screen.getByText('+$250')).toBeInTheDocument();
  });

  it('shows sources links', () => {
    render(<PolicyOverview />);
    expect(screen.getByText('S-4531 (P.L.2026, c.26)')).toBeInTheDocument();
    expect(
      screen.getByText('NJ Treasury FY2027 tax expenditure report (item 63)'),
    ).toBeInTheDocument();
  });
});
