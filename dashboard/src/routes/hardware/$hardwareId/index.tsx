import { createFileRoute } from '@tanstack/react-router';

import HardwareDetails from '@/pages/hardwareDetails/HardwareDetails';

export const Route = createFileRoute('/hardware/$hardwareId/')({
  component: HardwareDetails,
});
