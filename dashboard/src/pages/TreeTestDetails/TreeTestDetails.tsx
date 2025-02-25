import { useSearch } from '@tanstack/react-router';

import type { JSX } from 'react';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';

const TreeTestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/test/$testId/' });

  return (
    <TestDetails
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
