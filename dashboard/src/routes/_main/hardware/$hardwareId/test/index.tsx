import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/hardware/$hardwareId/test/')({
  component: () => <div>Hello /hardware/$hardware/test/!</div>,
});
