import { createFileRoute } from '@tanstack/react-router';

import HardwareV2 from '@/pages/Hardware/HardwareV2';

export const Route = createFileRoute('/_main/hardware/v2/')({
  component: () => (
    <HardwareV2
      urlFromMap={{ search: '/_main/hardware/v2', navigate: '/hardware/v2' }}
    />
  ),
});
