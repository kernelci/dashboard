import type { LinkProps } from '@tanstack/react-router';

import type { ColumnDef } from '@tanstack/react-table';

import { useIntl } from 'react-intl';

import { useMemo, type JSX } from 'react';

import Section from '@/components/Section/Section';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import type {
  AccordionItemBuilds,
  TableFilter,
  TableStatusOption,
} from '@/types/tree/TreeDetails';

import { useIssueDetailsBuilds } from '@/api/issueDetails';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import { defaultBuildColumns } from '@/components/BuildsTable/DefaultBuildsColumns';
import { TableHeader } from '@/components/Table/TableHeader';

import { sanitizeBuildTable } from '@/utils/utils';

interface IIssueDetailsBuildSection {
  issueId: string;
  versionNumber?: number;
  buildTableFilter: TableFilter['buildsTable'];
  onToggleFilter: (option: TableStatusOption) => void;
  getTableRowLink: (testId: string) => LinkProps;
}

const columns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.treeBranch" />
    ),
    cell: ({ row }): JSX.Element => (
      <span className="text-nowrap">{row.getValue('treeBranch')}</span>
    ),
  },
  ...defaultBuildColumns,
];

export const IssueDetailsBuildSection = ({
  issueId,
  versionNumber,
  buildTableFilter,
  onToggleFilter,
  getTableRowLink,
}: IIssueDetailsBuildSection): JSX.Element => {
  const { data, error, isLoading } = useIssueDetailsBuilds(
    issueId,
    versionNumber,
  );

  const { formatMessage } = useIntl();

  const buildData = useMemo((): AccordionItemBuilds[] => {
    if (!data) {
      return [];
    }
    return sanitizeBuildTable(data);
  }, [data]);

  if (!isLoading && error) {
    return <></>;
  }

  const body = data ? (
    <div className="flex flex-col gap-6">
      <BuildsTable
        tableKey="issueDetailsBuilds"
        buildItems={buildData}
        filter={buildTableFilter}
        getRowLink={getTableRowLink}
        onToggleFilter={onToggleFilter}
        columns={columns}
        sortKey="buildsTable"
      />
    </div>
  ) : (
    <MemoizedSectionError
      isLoading={isLoading}
      emptyLabel="issueDetails.noBuildResults"
    />
  );

  return (
    <Section
      title={formatMessage({ id: 'global.builds' })}
      subsections={[{ infos: [{ children: body }] }]}
    />
  );
};
