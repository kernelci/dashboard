import { useSearch } from '@tanstack/react-router';

import type { JSX } from 'react';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const HardwareTestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/test/$testId/' });

  return (
    <TestDetails
      breadcrumb={
        <MemoizedHardwareBreadcrumb
          searchParams={searchParams}
          locationMessage="test.details"
        />
      }
    />
  );
};

export default HardwareTestDetails;
