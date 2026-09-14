import { startOfTomorrow } from 'date-fns';
import { describe, expect, it } from 'vitest';

import {
  dateObjectToTimestampInSeconds,
  daysToSeconds,
  MILLISECONDS_IN_ONE_SECOND,
} from '@/utils/date';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import { resolveHardwareTimeRange } from './hardwareTimeRange';

const CUSTOM_INTERVAL_IN_DAYS = 30;

describe('resolveHardwareTimeRange', () => {
  it('returns explicit timestamps when both are provided', () => {
    const start = 1_700_000_000;
    const end = 1_700_500_000;

    expect(resolveHardwareTimeRange(REDUCED_TIME_SEARCH, start, end)).toEqual({
      startTimestampInSeconds: start,
      endTimestampInSeconds: end,
    });
  });

  it('defaults to a window ending after now', () => {
    const { startTimestampInSeconds, endTimestampInSeconds } =
      resolveHardwareTimeRange(REDUCED_TIME_SEARCH);
    const nowInSeconds = Math.floor(Date.now() / MILLISECONDS_IN_ONE_SECOND);

    expect(endTimestampInSeconds).toBe(
      dateObjectToTimestampInSeconds(startOfTomorrow()),
    );
    expect(endTimestampInSeconds).toBeGreaterThan(nowInSeconds);
    expect(startTimestampInSeconds).toBeLessThan(nowInSeconds);
  });

  it('sizes the window by the listing interval', () => {
    const end = 1_700_500_000;

    expect(
      resolveHardwareTimeRange(CUSTOM_INTERVAL_IN_DAYS, undefined, end),
    ).toEqual({
      startTimestampInSeconds: end - daysToSeconds(CUSTOM_INTERVAL_IN_DAYS),
      endTimestampInSeconds: end,
    });
  });
});
