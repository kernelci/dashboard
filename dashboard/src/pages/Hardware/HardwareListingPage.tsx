import { useMemo } from 'react';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import type {
  HardwareFastItem,
  HardwareListingItem,
  HardwareTableItem,
} from '@/types/hardware';

import { useHardwareListingFast, useHardwareListingSlow } from '@/api/Hardware';

import { HardwareTable } from './HardwareTable';

interface HardwareListingPageProps {
  inputFilter: string;
}

function isCompleteHardware(
  data: HardwareListingItem | HardwareFastItem,
): data is HardwareListingItem {
  return (
    'buildCount' in data &&
    'testStatusCount' in data &&
    'bootStatusCount' in data
  );
}

const HardwareListingPage = ({
  inputFilter,
}: HardwareListingPageProps): JSX.Element => {
  //TODO: Combine these 2 hooks inside a single hook
  const { data: fastData, status: fastStatus } = useHardwareListingFast();
  const { data, error, isLoading } = useHardwareListingSlow({
    enabled: fastStatus === 'success' && !!fastData,
  });

  const listItems: HardwareTableItem[] = useMemo(() => {
    if (!fastData || fastStatus === 'error') return [];

    const hasCompleteData = !isLoading && !!data;
    const currentData = hasCompleteData ? data.hardware : fastData.hardware;

    return currentData
      .filter(hardware => {
        return hardware.hardwareName?.includes(inputFilter);
      })
      .map((hardware): HardwareTableItem => {
        const buildCount = isCompleteHardware(hardware)
          ? {
              valid: hardware.buildCount?.valid,
              invalid: hardware.buildCount?.invalid,
              null: hardware.buildCount?.null,
            }
          : undefined;

        const testStatusCount = isCompleteHardware(hardware)
          ? {
              DONE: hardware.testStatusCount.DONE,
              ERROR: hardware.testStatusCount.ERROR,
              FAIL: hardware.testStatusCount.FAIL,
              MISS: hardware.testStatusCount.MISS,
              PASS: hardware.testStatusCount.PASS,
              SKIP: hardware.testStatusCount.SKIP,
              NULL: hardware.testStatusCount.NULL,
            }
          : undefined;

        const bootStatusCount = isCompleteHardware(hardware)
          ? {
              DONE: hardware.bootStatusCount.DONE,
              ERROR: hardware.bootStatusCount.ERROR,
              FAIL: hardware.bootStatusCount.FAIL,
              MISS: hardware.bootStatusCount.MISS,
              PASS: hardware.bootStatusCount.PASS,
              SKIP: hardware.bootStatusCount.SKIP,
              NULL: hardware.bootStatusCount.NULL,
            }
          : undefined;

        return {
          hardwareName: hardware.hardwareName ?? '',
          buildCount,
          testStatusCount,
          bootStatusCount,
        };
      })
      .sort((a, b) => a.hardwareName.localeCompare(b.hardwareName));
  }, [data, fastData, inputFilter, isLoading, fastStatus]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <QuerySwitcher status={fastStatus} data={fastData}>
      <Toaster />
      <div className="flex flex-col gap-6">
        <HardwareTable treeTableRows={listItems} />
      </div>
    </QuerySwitcher>
  );
};

export default HardwareListingPage;
