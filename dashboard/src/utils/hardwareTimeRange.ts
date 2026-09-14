import { startOfTomorrow } from 'date-fns';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';

/** Default hardware window: [tomorrow - intervalInDays, tomorrow), shared by listing and details. */
export const resolveHardwareTimeRange = (
  intervalInDays: number,
  startTimestampInSeconds?: number,
  endTimestampInSeconds?: number,
): {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
} => {
  const end =
    endTimestampInSeconds ?? dateObjectToTimestampInSeconds(startOfTomorrow());

  return {
    startTimestampInSeconds:
      startTimestampInSeconds ?? end - daysToSeconds(intervalInDays),
    endTimestampInSeconds: end,
  };
};
