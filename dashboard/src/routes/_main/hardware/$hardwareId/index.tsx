import { createFileRoute } from '@tanstack/react-router';

import HardwareDetails from '@/pages/hardwareDetails/HardwareDetails';

export const Route = createFileRoute('/_main/hardware/$hardwareId/')({
  component: HardwareDetails,
});
