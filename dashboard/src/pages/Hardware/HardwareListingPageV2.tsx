import { useEffect, useMemo, useState, type JSX } from 'react';
import { roundToNearestMinutes } from 'date-fns';

import { useSearch } from '@tanstack/react-router';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareItem } from '@/types/hardware';

import { useHardwareListingV2 } from '@/api/hardware';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';

import type { RequiredStatusCount, StatusCount } from '@/types/general';

import {
  matchesRegexOrIncludes,
  includesInAnStringOrStringArray,
} from '@/lib/string';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { HardwareTable } from './HardwareTable';

interface HardwareListingPageV2Props {
  inputFilter: string;
}

const calculateTimeStamp = (
  intervalInDays: number,
): {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
} => {
  // Rounding so cache key doesn't get invalidated every request
  const endTimestampInSeconds = dateObjectToTimestampInSeconds(
    roundToNearestMinutes(new Date(), {
      nearestTo: 30,
    }),
  );
  const startTimestampInSeconds =
    endTimestampInSeconds - daysToSeconds(intervalInDays);
  return { startTimestampInSeconds, endTimestampInSeconds };
};

const useHardwareListingTime = (): {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
} => {
  const { intervalInDays } = useSearch({ from: '/_main/hardware' });
  const [timestamps, setTimeStamps] = useState(() => {
    return calculateTimeStamp(intervalInDays);
  });

  useEffect(() => {
    setTimeStamps(calculateTimeStamp(intervalInDays));
  }, [intervalInDays]);

  const { startTimestampInSeconds, endTimestampInSeconds } = timestamps;

  return { startTimestampInSeconds, endTimestampInSeconds };
};

const HardwareListingPageV2 = ({
  inputFilter,
}: HardwareListingPageV2Props): JSX.Element => {
  const { startTimestampInSeconds, endTimestampInSeconds } =
    useHardwareListingTime();
  const { origin } = useSearch({ from: '/_main/hardware' });

  const { data, error, status, isLoading } = useHardwareListingV2(
    startTimestampInSeconds,
    endTimestampInSeconds,
  );

  const listItems: HardwareItem[] = useMemo(() => {
    if (!data || error) {
      return [];
    }

    const currentData = data.hardware;

    return currentData
      .filter(hardware => {
        return (
          matchesRegexOrIncludes(hardware.platform, inputFilter) ||
          includesInAnStringOrStringArray(hardware.hardware ?? '', inputFilter)
        );
      })
      .map((hardware): HardwareItem => {
        const buildCount: RequiredStatusCount = {
          PASS: hardware.build_status_summary?.PASS,
          FAIL: hardware.build_status_summary?.FAIL,
          NULL: 0,
          ERROR: 0,
          MISS: 0,
          DONE: 0,
          SKIP: hardware.build_status_summary?.INCONCLUSIVE,
        };

        const testStatusCount: StatusCount = {
          DONE: 0,
          ERROR: 0,
          FAIL: hardware.test_status_summary.FAIL,
          MISS: 0,
          PASS: hardware.test_status_summary.PASS,
          SKIP: 0,
          NULL: hardware.test_status_summary.INCONCLUSIVE,
        };

        const bootStatusCount: StatusCount = {
          DONE: 0,
          ERROR: 0,
          FAIL: hardware.boot_status_summary.FAIL,
          MISS: 0,
          PASS: hardware.boot_status_summary.PASS,
          SKIP: 0,
          NULL: hardware.boot_status_summary.INCONCLUSIVE,
        };

        return {
          hardware: hardware.hardware,
          platform: hardware.platform,
          build_status_summary: buildCount,
          test_status_summary: testStatusCount,
          boot_status_summary: bootStatusCount,
        };
      })
      .sort((a, b) => a.platform.localeCompare(b.platform));
  }, [data, error, inputFilter]);

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="hardwareListing"
        args={{ cmdName: 'hardware list', origin: origin, json: true }}
      />
    ),
    [origin],
  );

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        <HardwareTable
          treeTableRows={listItems}
          endTimestampInSeconds={endTimestampInSeconds}
          startTimestampInSeconds={startTimestampInSeconds}
          status={status}
          queryData={data}
          error={error}
          isLoading={isLoading}
          navigateFrom="/hardware"
        />
      </div>
      {kcidevComponent}
    </>
  );
};

export default HardwareListingPageV2;
