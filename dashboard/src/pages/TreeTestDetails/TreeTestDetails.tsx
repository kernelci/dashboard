import { useParams, useSearch } from '@tanstack/react-router';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';

const TreeTestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/test/$testId/' });
  const { testId } = useParams({ from: '/test/$testId/' });

  return (
    <TestDetails
      testId={testId}
      breadcrumb={
        <MemoizedTreeBreadcrumb
          searchParams={searchParams}
          locationMessage="test.details"
        />
      }
    />
  );
};

export default TreeTestDetails;
