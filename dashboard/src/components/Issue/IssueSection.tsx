import { useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { UseQueryResult } from '@tanstack/react-query';

import { Link } from '@tanstack/react-router';

import ListingItem from '@/components/ListingItem/ListingItem';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { TErrorVariant } from '@/components/DetailsPages/SectionError';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { TIssue } from '@/types/issues';

import { IssueTooltip } from './IssueTooltip';

const IssueSection = ({
  data,
  status,
  error,
  variant = 'error',
}: {
  data?: TIssue[];
  status: UseQueryResult['status'];
  error?: string;
  variant?: TErrorVariant;
}): JSX.Element => {
  const issueList = useMemo(
    () =>
      data?.map(issue => {
        return (
          <Link
            key={issue.id + issue.version}
            className="mb-16 flex not-last:mb-2 not-last:border-b not-last:pb-2"
            to="/issue/$issueId"
            params={{ issueId: issue.id }}
            state={s => s}
            search={s => ({
              origin: s.origin,
              issueVersion: issue.version,
            })}
          >
            <ListingItem
              unknown={issue.incidents_info.incidentsCount}
              text={issue.comment ?? issue.id}
              tooltip={issue.id}
            />
          </Link>
        );
      }),
    [data],
  );

  return (
    <div>
      <div className="mb-3 flex items-center gap-4 border-b border-gray-300 pb-3">
        <h2 className="text-2xl font-semibold">
          <FormattedMessage id="global.issues" />
        </h2>
        <IssueTooltip />
      </div>
      <QuerySwitcher
        skeletonClassname="h-[100px]"
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={status === 'pending'}
            errorMessage={error}
            emptyLabel="issue.noIssueFound"
            variant={variant}
          />
        }
      >
        {issueList}
      </QuerySwitcher>
    </div>
  );
};

export default IssueSection;
