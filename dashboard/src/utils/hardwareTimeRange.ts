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
  const span = daysToSeconds(intervalInDays);

  if (
    startTimestampInSeconds !== undefined &&
    endTimestampInSeconds !== undefined
  ) {
    return {
      startTimestampInSeconds,
      endTimestampInSeconds,
    };
  }

  if (startTimestampInSeconds !== undefined) {
    return {
      startTimestampInSeconds,
      endTimestampInSeconds: startTimestampInSeconds + span,
    };
  }

  if (endTimestampInSeconds !== undefined) {
    return {
      startTimestampInSeconds: endTimestampInSeconds - span,
      endTimestampInSeconds,
    };
  }

  const end = dateObjectToTimestampInSeconds(startOfTomorrow());
  return {
    startTimestampInSeconds: end - span,
    endTimestampInSeconds: end,
  };
};
