import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/test/')({
  component: () => <div>Hello /hardware/$hardware/test/!</div>,
});
