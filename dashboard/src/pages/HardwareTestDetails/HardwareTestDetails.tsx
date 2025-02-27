import type { JSX } from 'react';

import { useSearchStore } from '@/hooks/store/useSearchStore';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const HardwareTestDetails = (): JSX.Element => {
  const previousSearch = useSearchStore(s => s.previousSearch);

  return (
    <TestDetails
      breadcrumb={
        <MemoizedHardwareBreadcrumb
          searchParams={previousSearch}
          locationMessage="test.details"
        />
      }
    />
  );
};

export default HardwareTestDetails;
