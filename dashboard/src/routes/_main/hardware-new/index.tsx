import { createFileRoute } from '@tanstack/react-router';

import Hardware from '@/pages/HardwareNew/Hardware';

export const Route = createFileRoute('/_main/hardware-new/')({
  component: Hardware,
});
