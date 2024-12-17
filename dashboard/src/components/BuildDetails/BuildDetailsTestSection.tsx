import { FormattedMessage, useIntl } from 'react-intl';

import { RiProhibited2Line } from 'react-icons/ri';

import type { HistoryState, LinkProps } from '@tanstack/react-router';

import { Separator } from '@/components/ui/separator';

import { useBuildTests } from '@/api/buildTests';

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';

interface IBuildDetailsTestSection {
  buildId: string;
  onClickFilter: (filter: TestsTableFilter) => void;
  tableFilter: TableFilter;
  getRowLink: (testId: string) => LinkProps;
  historyState?: HistoryState;
}

const NoTestFound = (): JSX.Element => (
  <div className="flex flex-col items-center py-6 text-weakGray">
    <RiProhibited2Line className="h-14 w-14" />
    <h1 className="text-2xl font-semibold">
      <FormattedMessage id={'buildDetails.noTestResults'} />
    </h1>
  </div>
);

const BuildDetailsTestSection = ({
  buildId,
  onClickFilter,
  tableFilter,
  getRowLink,
  historyState,
}: IBuildDetailsTestSection): JSX.Element => {
  const intl = useIntl();
  const { data, error } = useBuildTests(buildId);

  const hasTest = data && data.length > 0 && !error;
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
        <NoTestFound />
      )}
    </>
  );
};

export default BuildDetailsTestSection;
