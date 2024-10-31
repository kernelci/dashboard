import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/build/$buildId/')({
  component: () => <div>Hello /hardware/$hardware/build/$buildId/!</div>,
});
