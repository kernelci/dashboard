import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/hardware/$hardwareId/build/')({
  component: () => <div>Hello /hardware/$hardware/build/!</div>,
});
