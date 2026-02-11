import { createFileRoute } from '@tanstack/react-router';

import Hardware from '@/pages/Hardware';

export const Route = createFileRoute('/_main/hardware/v1/')({
  component: () => (
    <Hardware
      urlFromMap={{ search: '/_main/hardware/v1', navigate: '/hardware/v1' }}
    />
  ),
});
