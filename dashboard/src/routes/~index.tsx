import { createFileRoute } from '@tanstack/react-router';

import Trees from '../pages/Trees';

export const Route = createFileRoute('/')({
  component: Trees,
});
