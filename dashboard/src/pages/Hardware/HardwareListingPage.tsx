import { useEffect, useMemo, useState } from 'react';
import { roundToNearestMinutes } from 'date-fns';

import { useSearch } from '@tanstack/react-router';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareTableItem } from '@/types/hardware';

import { useHardwareListing } from '@/api/hardware';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';

import { HardwareTable } from './HardwareTable';

interface HardwareListingPageProps {
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
  const { intervalInDays } = useSearch({ from: '/hardware' });
  const [timestamps, setTimeStamps] = useState(() => {
    return calculateTimeStamp(intervalInDays);
  });

  useEffect(() => {
    setTimeStamps(calculateTimeStamp(intervalInDays));
  }, [intervalInDays]);

  const { startTimestampInSeconds, endTimestampInSeconds } = timestamps;

  return { startTimestampInSeconds, endTimestampInSeconds };
};

const HardwareListingPage = ({
  inputFilter,
}: HardwareListingPageProps): JSX.Element => {
  const { startTimestampInSeconds, endTimestampInSeconds } =
    useHardwareListingTime();

  const { data, error, status } = useHardwareListing(
    startTimestampInSeconds,
    endTimestampInSeconds,
  );

  const listItems: HardwareTableItem[] = useMemo(() => {
    if (!data || error) return [];

    const currentData = data.hardware;

    return currentData
      .filter(hardware => {
        return hardware.hardwareName?.includes(inputFilter);
      })
      .map((hardware): HardwareTableItem => {
        const buildCount = {
          valid: hardware.buildCount?.valid,
          invalid: hardware.buildCount?.invalid,
          null: hardware.buildCount?.null,
        };

        const testStatusCount = {
          DONE: hardware.testStatusCount.DONE,
          ERROR: hardware.testStatusCount.ERROR,
          FAIL: hardware.testStatusCount.FAIL,
          MISS: hardware.testStatusCount.MISS,
          PASS: hardware.testStatusCount.PASS,
          SKIP: hardware.testStatusCount.SKIP,
          NULL: hardware.testStatusCount.NULL,
        };

        const bootStatusCount = {
          DONE: hardware.bootStatusCount.DONE,
          ERROR: hardware.bootStatusCount.ERROR,
          FAIL: hardware.bootStatusCount.FAIL,
          MISS: hardware.bootStatusCount.MISS,
          PASS: hardware.bootStatusCount.PASS,
          SKIP: hardware.bootStatusCount.SKIP,
          NULL: hardware.bootStatusCount.NULL,
        };

        return {
          hardwareName: hardware.hardwareName ?? '',
          buildCount,
          testStatusCount,
          bootStatusCount,
        };
      })
      .sort((a, b) => a.hardwareName.localeCompare(b.hardwareName));
  }, [data, error, inputFilter]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <QuerySwitcher status={status} data={data}>
      <Toaster />
      <div className="flex flex-col gap-6">
        <HardwareTable
          treeTableRows={listItems}
          endTimestampInSeconds={endTimestampInSeconds}
          startTimestampInSeconds={startTimestampInSeconds}
        />
      </div>
    </QuerySwitcher>
  );
};

export default HardwareListingPage;
