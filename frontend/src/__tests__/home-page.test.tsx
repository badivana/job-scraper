import { render, screen } from '@testing-library/react';
import Home from '../app/page';

test('renders homepage', () => {
  render(<Home />);
  const heading = screen.getByRole('heading', { name: /ai job finder/i });
  expect(heading).toBeInTheDocument();
});