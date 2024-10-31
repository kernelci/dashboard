import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/hardware/$hardwareId/test/$testId/')({
  component: () => <div>Hello /hardware/$hardware/test/$testId/!</div>,
});
