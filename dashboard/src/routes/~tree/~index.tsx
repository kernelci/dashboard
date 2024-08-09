import { createFileRoute } from '@tanstack/react-router';

import Trees from './Trees';

export const Route = createFileRoute('/tree/')({
  component: Trees,
});
