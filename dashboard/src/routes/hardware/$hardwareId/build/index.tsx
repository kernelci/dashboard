import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/build/')({
  component: () => <div>Hello /hardware/$hardware/build/!</div>,
});
