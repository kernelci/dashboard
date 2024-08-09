import { createFileRoute } from '@tanstack/react-router';

import Trees from './~tree/Trees';

export const Route = createFileRoute('/')({
  component: Trees,
});
