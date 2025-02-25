import { createFileRoute } from '@tanstack/react-router';

import IssueListing from '@/pages/IssueListing/IssueListing';

export const Route = createFileRoute('/_main/issue/')({
  component: IssueListing,
});
