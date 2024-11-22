import { useEffect, useMemo, useState } from 'react';

import { useSearch } from '@tanstack/react-router';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareTableItem } from '@/types/hardware';

import { useHardwareListing } from '@/api/Hardware';

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
  const endTimestampInSeconds = dateObjectToTimestampInSeconds(new Date());
  const startTimestampInSeconds =
    endTimestampInSeconds - daysToSeconds(intervalInDays);
  return { startTimestampInSeconds, endTimestampInSeconds };
};

const HardwareListingPage = ({
  inputFilter,
}: HardwareListingPageProps): JSX.Element => {
  //TODO: Combine these 2 hooks inside a single hook
  const { intervalInDays } = useSearch({ from: '/hardware' });
  const [timestamps, setTimeStamps] = useState(() => {
    return calculateTimeStamp(intervalInDays);
  });

  const { startTimestampInSeconds, endTimestampInSeconds } = timestamps;

  useEffect(() => {
    setTimeStamps(calculateTimeStamp(intervalInDays));
  }, [intervalInDays]);

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
          startTimestampInSeconds={startTimestampInSeconds}
          endTimestampInSeconds={endTimestampInSeconds}
        />
      </div>
    </QuerySwitcher>
  );
};

export default HardwareListingPage;
