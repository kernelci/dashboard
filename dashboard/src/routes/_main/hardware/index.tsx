import { createFileRoute } from '@tanstack/react-router';

import HardwareV2 from '@/pages/Hardware/HardwareV2';

export const Route = createFileRoute('/_main/hardware/')({
  component: HardwareV2,
});
