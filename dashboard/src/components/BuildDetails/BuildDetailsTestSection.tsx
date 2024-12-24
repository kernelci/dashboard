import { useIntl } from 'react-intl';

import type { HistoryState, LinkProps } from '@tanstack/react-router';

import { Separator } from '@/components/ui/separator';

import { useBuildTests } from '@/api/buildTests';

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

interface IBuildDetailsTestSection {
  buildId: string;
  onClickFilter: (filter: TestsTableFilter) => void;
  tableFilter: TableFilter;
  getRowLink: (testId: string) => LinkProps;
  historyState?: HistoryState;
}

const BuildDetailsTestSection = ({
  buildId,
  onClickFilter,
  tableFilter,
  getRowLink,
  historyState,
}: IBuildDetailsTestSection): JSX.Element => {
  const intl = useIntl();
  const { data, error, isLoading } = useBuildTests(buildId);

  const hasTest = data && data.length > 0;
  return (
    <>
      <span className="text-2xl font-bold">
        {intl.formatMessage({ id: 'buildDetails.testResults' })}
      </span>
      <Separator className="my-6 bg-darkGray" />
      {hasTest ? (
        <div className="flex flex-col gap-6">
          <TestsTable
            tableKey="buildDetailsTests"
            testHistory={data}
            onClickFilter={onClickFilter}
            filter={tableFilter.testsTable}
            getRowLink={getRowLink}
            historyState={historyState}
          />
        </div>
      ) : (
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          isEmpty={data?.length === 0}
          emptyLabel={'buildDetails.noTestResults'}
        />
      )}
    </>
  );
};

export default BuildDetailsTestSection;
