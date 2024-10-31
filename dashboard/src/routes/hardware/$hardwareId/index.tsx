import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/')({
  component: () => <div>Hello /hardware/$hardware/!</div>,
});
