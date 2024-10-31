import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/')({
  component: () => <div>Hello /hardware/!</div>,
});
