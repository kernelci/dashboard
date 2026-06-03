import { createFileRoute } from '@tanstack/react-router';

import Hardware from '@/pages/Hardware/Hardware';

export const Route = createFileRoute('/_main/hardware/')({
  component: () => (
    <Hardware
      urlFromMap={{ search: '/_main/hardware', navigate: '/hardware' }}
    />
  ),
});
