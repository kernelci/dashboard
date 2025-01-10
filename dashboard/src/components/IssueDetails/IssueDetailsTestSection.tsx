import type { LinkProps } from '@tanstack/react-router';

import { useIntl } from 'react-intl';

import { useIssueDetailsTests } from '@/api/issueDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import { Separator } from '@/components/ui/separator';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';

interface IIssueDetailsTestSection {
  issueId: string;
  versionNumber: string;
  testTableFilter: TableFilter['testsTable'];
  onClickFilter: (filter: TestsTableFilter) => void;
  getTableRowLink: (testId: string) => LinkProps;
}

export const IssueDetailsTestSection = ({
  issueId,
  versionNumber,
  testTableFilter,
  onClickFilter,
  getTableRowLink,
}: IIssueDetailsTestSection): JSX.Element => {
  const { data, error, isLoading } = useIssueDetailsTests(
    issueId,
    versionNumber,
  );
  const { formatMessage } = useIntl();

  if (!isLoading && data?.length === 0) {
    return <></>;
  }

  return (
    <>
      <h2 className="text-2xl font-bold">
        {formatMessage({ id: 'global.tests' })}
      </h2>
      <Separator className="my-6 bg-darkGray" />
      {data ? (
        <div className="flex flex-col gap-6">
          <TestsTable
            tableKey="issueDetailsTests"
            testHistory={data}
            onClickFilter={onClickFilter}
            filter={testTableFilter}
            getRowLink={getTableRowLink}
          />
        </div>
      ) : (
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
        />
      )}
    </>
  );
};
