import { useMemo } from 'react';

import { useSearch } from '@tanstack/react-router';

import { resolveHardwareTimeRange } from '@/utils/hardwareTimeRange';

export const useHardwareDetailsTimeRange = (): {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
} => {
  const { intervalInDays, startTimestampInSeconds, endTimestampInSeconds } =
    useSearch({ from: '/_main/hardware/$hardwareId/' });

  return useMemo(
    () =>
      resolveHardwareTimeRange(
        intervalInDays,
        startTimestampInSeconds,
        endTimestampInSeconds,
      ),
    [intervalInDays, startTimestampInSeconds, endTimestampInSeconds],
  );
};
