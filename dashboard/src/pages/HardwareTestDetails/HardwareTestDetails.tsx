import { useParams, useSearch } from '@tanstack/react-router';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const HardwareTestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/test/$testId/' });
  const { testId } = useParams({ from: '/test/$testId/' });

  return (
    <TestDetails
      testId={testId}
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
