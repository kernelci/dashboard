import { createFileRoute } from '@tanstack/react-router';

import Hardware from '@/pages/Hardware';

export const Route = createFileRoute('/hardware/')({
  component: Hardware,
});
