import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/boot/$bootId/')({
  component: () => <div>Hello /hardware/$hardware/boot/$bootId/!</div>,
});
