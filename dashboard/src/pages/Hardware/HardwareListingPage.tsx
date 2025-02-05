import { useEffect, useMemo, useState } from 'react';
import { roundToNearestMinutes } from 'date-fns';

import { useSearch } from '@tanstack/react-router';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareTableItem } from '@/types/hardware';

import { useHardwareListing } from '@/api/hardware';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { BuildStatus, StatusCount } from '@/types/general';

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

const includesInAnStringOrArray = (
  searched: string | string[],
  inputFilter: string,
): boolean => {
  if (Array.isArray(searched)) {
    return searched.some(element => element.includes(inputFilter));
  }
  return searched.includes(inputFilter);
};

const HardwareListingPage = ({
  inputFilter,
}: HardwareListingPageProps): JSX.Element => {
  const { startTimestampInSeconds, endTimestampInSeconds } =
    useHardwareListingTime();

  const { data, error, status, isLoading } = useHardwareListing(
    startTimestampInSeconds,
    endTimestampInSeconds,
  );

  const listItems: HardwareTableItem[] = useMemo(() => {
    if (!data || error) {
      return [];
    }

    const currentData = data.hardware;

    return currentData
      .filter(hardware => {
        return (
          hardware.hardware_name?.includes(inputFilter) ||
          includesInAnStringOrArray(hardware.platform, inputFilter)
        );
      })
      .map((hardware): HardwareTableItem => {
        const buildCount: BuildStatus = {
          valid: hardware.build_status_summary?.valid,
          invalid: hardware.build_status_summary?.invalid,
          null: hardware.build_status_summary?.null,
        };

        const testStatusCount: StatusCount = {
          DONE: hardware.test_status_summary.DONE,
          ERROR: hardware.test_status_summary.ERROR,
          FAIL: hardware.test_status_summary.FAIL,
          MISS: hardware.test_status_summary.MISS,
          PASS: hardware.test_status_summary.PASS,
          SKIP: hardware.test_status_summary.SKIP,
          NULL: hardware.test_status_summary.NULL,
        };

        const bootStatusCount: StatusCount = {
          DONE: hardware.boot_status_summary.DONE,
          ERROR: hardware.boot_status_summary.ERROR,
          FAIL: hardware.boot_status_summary.FAIL,
          MISS: hardware.boot_status_summary.MISS,
          PASS: hardware.boot_status_summary.PASS,
          SKIP: hardware.boot_status_summary.SKIP,
          NULL: hardware.boot_status_summary.NULL,
        };

        return {
          hardware_name: hardware.hardware_name ?? '',
          platform: hardware.platform ?? '',
          build_status_summary: buildCount,
          test_status_summary: testStatusCount,
          boot_status_summary: bootStatusCount,
        };
      })
      .sort((a, b) => a.hardware_name.localeCompare(b.hardware_name));
  }, [data, error, inputFilter]);

  return (
    <QuerySwitcher
      status={status}
      data={data}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          emptyLabel={'global.error'}
        />
      }
    >
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
