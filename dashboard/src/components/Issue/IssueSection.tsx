import { useMemo, type JSX } from 'react';

import { useIntl } from 'react-intl';

import type { UseQueryResult } from '@tanstack/react-query';

import { Link } from '@tanstack/react-router';

import ListingItem from '@/components/ListingItem/ListingItem';
import Section from '@/components/Section/Section';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { TErrorVariant } from '@/components/DetailsPages/SectionError';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { TIssue } from '@/types/issues';

import { groupStatus } from '@/utils/status';

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
  const { formatMessage } = useIntl();
  const issueList = useMemo(
    () =>
      data?.map(issue => {
        const counts = issue.incidents_info;
        const groupedCount = groupStatus({
          passCount: counts.PASS,
          failCount: counts.FAIL,
          nullCount: counts.NULL,
          errorCount: counts.ERROR,
          missCount: counts.MISS,
          doneCount: counts.DONE,
          skipCount: counts.SKIP,
        });
        const totalCount =
          groupedCount.successCount +
          groupedCount.failedCount +
          groupedCount.inconclusiveCount;
        return (
          <Link
            key={issue.id + issue.version}
            className="mb-12 flex not-last:mb-2 not-last:border-b not-last:pb-2"
            to="/issue/$issueId"
            params={{ issueId: issue.id }}
            state={s => s}
            search={s => ({
              origin: s.origin,
              issueVersion: issue.version,
            })}
          >
            <ListingItem
              unknown={totalCount}
              text={issue.comment ?? issue.id}
              tooltip={issue.id}
            />
          </Link>
        );
      }),
    [data],
  );

  return (
    <Section
      title={formatMessage({ id: 'global.issues' })}
      rightIcon={<IssueTooltip />}
      subsections={[
        {
          infos: [
            {
              children: (
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
              ),
            },
          ],
        },
      ]}
    />
  );
};

export default IssueSection;
