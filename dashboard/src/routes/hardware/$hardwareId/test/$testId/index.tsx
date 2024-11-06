import { createFileRoute } from '@tanstack/react-router';

import HardwareTestDetails from '@/pages/HardwareTestDetails';

export const Route = createFileRoute('/hardware/$hardwareId/test/$testId/')({
  component: () => <HardwareTestDetails />,
});
