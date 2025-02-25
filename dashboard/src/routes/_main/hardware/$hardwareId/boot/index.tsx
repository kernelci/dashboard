import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/hardware/$hardwareId/boot/')({
  component: () => <div>Hello /hardware/$hardware/boot/!</div>,
});
