import type { LinkProps } from '@tanstack/react-router';

import type { ColumnDef } from '@tanstack/react-table';

import { useIntl } from 'react-intl';

import { useIssueDetailsTests } from '@/api/issueDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import { defaultInnerColumns } from '@/components/TestsTable/DefaultTestsColumns';
import { TableHeader } from '@/components/Table/TableHeader';

import { Separator } from '@/components/ui/separator';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';
import type { TIndividualTest } from '@/types/general';

interface IIssueDetailsTestSection {
  issueId: string;
  versionNumber?: number;
  testTableFilter: TableFilter['testsTable'];
  onClickFilter: (filter: TestsTableFilter) => void;
  getTableRowLink: (testId: string) => LinkProps;
}

const innerColumns: ColumnDef<TIndividualTest>[] = [
  defaultInnerColumns[0],
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="hardwareDetails.treeBranch" />
    ),
  },
  ...defaultInnerColumns.slice(1),
];

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

  if (!isLoading && error) {
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
            innerColumns={innerColumns}
          />
        </div>
      ) : (
        <MemoizedSectionError isLoading={isLoading} />
      )}
    </>
  );
};
