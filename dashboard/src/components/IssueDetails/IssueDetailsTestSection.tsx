import type { LinkProps } from '@tanstack/react-router';

import type { ColumnDef } from '@tanstack/react-table';

import { useIntl } from 'react-intl';

import type { JSX } from 'react';

import { useIssueDetailsTests } from '@/api/issueDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import { defaultInnerColumns } from '@/components/TestsTable/DefaultTestsColumns';
import { TableHeader } from '@/components/Table/TableHeader';

import Section from '@/components/Section/Section';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { TableFilter, TableStatusOption } from '@/types/tree/TreeDetails';
import type { TIndividualTest } from '@/types/general';

interface IIssueDetailsTestSection {
  issueId: string;
  versionNumber?: number;
  testTableFilter: TableFilter['testsTable'];
  onToggleFilter: (option: TableStatusOption) => void;
  getTableRowLink: (testId: string) => LinkProps;
}

const innerColumns: ColumnDef<TIndividualTest>[] = [
  defaultInnerColumns[0],
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.treeBranch" />
    ),
    cell: ({ row }): JSX.Element => (
      <span className="text-nowrap">{row.getValue('treeBranch')}</span>
    ),
  },
  ...defaultInnerColumns.slice(1),
];

export const IssueDetailsTestSection = ({
  issueId,
  versionNumber,
  testTableFilter,
  onToggleFilter,
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

  const body = data ? (
    <TestsTable
      tableKey="issueDetailsTests"
      testHistory={data}
      onToggleFilter={onToggleFilter}
      filter={testTableFilter}
      getRowLink={getTableRowLink}
      innerColumns={innerColumns}
      sortKey="testsTable"
    />
  ) : (
    <MemoizedSectionError
      isLoading={isLoading}
      emptyLabel="issueDetails.noTestResults"
    />
  );

  return (
    <Section
      title={formatMessage({ id: 'global.tests' })}
      subsections={[{ infos: [{ children: body }] }]}
    />
  );
};
