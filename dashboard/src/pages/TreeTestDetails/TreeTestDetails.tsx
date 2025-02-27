import type { JSX } from 'react';

import { useSearchStore } from '@/hooks/store/useSearchStore';

import TestDetails from '@/components/TestDetails/TestDetails';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';

const TreeTestDetails = (): JSX.Element => {
  const previousSearch = useSearchStore(s => s.previousSearch);

  return (
    <TestDetails
      breadcrumb={
        <MemoizedTreeBreadcrumb
          searchParams={previousSearch}
          locationMessage="test.details"
        />
      }
    />
  );
};

export default TreeTestDetails;
