import { createFileRoute } from '@tanstack/react-router';

import type { JSX } from 'react';

import HardwareV2 from '@/pages/Hardware/HardwareV2';
import Hardware from '@/pages/Hardware/Hardware';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';

const HardwareListingComponent = (): JSX.Element => {
  const { hardwareListingVersion } = useFeatureFlag();
  return hardwareListingVersion === 'v2' ? (
    <HardwareV2
      urlFromMap={{ search: '/_main/hardware', navigate: '/hardware' }}
    />
  ) : (
    <Hardware
      urlFromMap={{ search: '/_main/hardware', navigate: '/hardware' }}
    />
  );
};

export const Route = createFileRoute('/_main/hardware/')({
  component: HardwareListingComponent,
});
