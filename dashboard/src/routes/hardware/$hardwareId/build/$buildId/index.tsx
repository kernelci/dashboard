import { createFileRoute } from '@tanstack/react-router';

import HardwareBuildDetails from '@/pages/HardwareBuildDetails';

export const Route = createFileRoute('/hardware/$hardwareId/build/$buildId/')({
  component: () => <HardwareBuildDetails />,
});
