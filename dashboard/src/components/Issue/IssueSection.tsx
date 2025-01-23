import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { UseQueryResult } from '@tanstack/react-query';

import type { HistoryState, LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import { RiProhibited2Line } from 'react-icons/ri';

import ListingItem from '@/components/ListingItem/ListingItem';
import type { TIssue } from '@/types/general';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

export const NoIssueFound = (): JSX.Element => {
  return (
    <div className="flex flex-col items-center py-6 text-weakGray">
      <RiProhibited2Line className="h-14 w-14" />
      <h1 className="text-2xl font-semibold">
        <FormattedMessage id={'issue.noIssueFound'} />
      </h1>
    </div>
  );
};

const IssueSection = ({
  data,
  status,
  error,
  historyState,
  previousSearch,
}: {
  data?: TIssue[];
  status: UseQueryResult['status'];
  error?: string;
  historyState?: HistoryState;
  previousSearch: LinkProps['search'];
}): JSX.Element => {
  const issueList = useMemo(
    () =>
      data?.map(issue => (
        <Link
          key={issue.id + issue.version}
          className="mb-16 flex [&:not(:last-child)]:mb-2 [&:not(:last-child)]:border-b [&:not(:last-child)]:pb-2"
          to="/issue/$issueId/version/$versionNumber"
          params={{ issueId: issue.id, versionNumber: issue.version }}
          state={historyState}
          search={previousSearch}
        >
          <ListingItem
            unknown={issue.incidents_info.incidentsCount}
            text={issue.comment ?? issue.id}
            tooltip={issue.id}
          />
        </Link>
      )),
    [data, historyState, previousSearch],
  );

  return (
    <div>
      <h2 className="mb-3 border-b border-gray-300 pb-3 text-2xl font-semibold">
        <FormattedMessage id="global.issues" />
      </h2>
      <QuerySwitcher
        skeletonClassname="h-[100px]"
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={status === 'pending'}
            errorMessage={error}
            emptyLabel={'global.error'}
          />
        }
      >
        {issueList}
      </QuerySwitcher>
    </div>
  );
};

export default IssueSection;
