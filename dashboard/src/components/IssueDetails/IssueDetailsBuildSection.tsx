import type { LinkProps } from '@tanstack/react-router';

import { useIntl } from 'react-intl';

import { useMemo } from 'react';

import { Separator } from '@/components/ui/separator';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import type {
  AccordionItemBuilds,
  BuildsTableFilter,
  TableFilter,
} from '@/types/tree/TreeDetails';

import { useIssueDetailsBuilds } from '@/api/issueDetails';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import { sanitizeBuildTable } from '@/utils/utils';
import { NOT_FOUND_STATUS } from '@/types/issueDetails';

interface IIssueDetailsBuildSection {
  issueId: string;
  versionNumber: string;
  buildTableFilter: TableFilter['buildsTable'];
  onClickFilter: (filter: BuildsTableFilter) => void;
  getTableRowLink: (testId: string) => LinkProps;
}

export const IssueDetailsBuildSection = ({
  issueId,
  versionNumber,
  buildTableFilter,
  onClickFilter,
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

  if (!isLoading && error?.status === NOT_FOUND_STATUS) {
    return <></>;
  }

  return (
    <>
      <h2 className="text-2xl font-bold">
        {formatMessage({ id: 'global.builds' })}
      </h2>
      <Separator className="my-6 bg-darkGray" />
      {data ? (
        <div className="flex flex-col gap-6">
          <BuildsTable
            tableKey="issueDetailsBuilds"
            buildItems={buildData}
            filter={buildTableFilter}
            getRowLink={getTableRowLink}
            onClickFilter={onClickFilter}
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
