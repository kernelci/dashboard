import { useMemo } from 'react';

import { FaRegCircle, FaRegDotCircle } from 'react-icons/fa';

import { FormattedMessage } from 'react-intl';

import { UseQueryResult } from '@tanstack/react-query';

import { Link } from '@tanstack/react-router';

import { RiProhibited2Line } from 'react-icons/ri';

import ListingItem from '@/components/ListingItem/ListingItem';
import { TIssue } from '@/types/general';

import QuerySwitcher from '../QuerySwitcher/QuerySwitcher';

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
}: UseQueryResult<TIssue[]>): JSX.Element => {
  const issueList = useMemo(
    () =>
      data?.map(issue => (
        <Link
          key={issue.incident_id}
          to={issue.report_url}
          target="_blank"
          className="flex [&:not(:last-child)]:mb-2 [&:not(:last-child)]:border-b [&:not(:last-child)]:pb-2"
        >
          <ListingItem
            text={issue.comment ?? ''}
            leftIcon={
              <div className="text-darkGray2">
                {issue.present ? <FaRegDotCircle /> : <FaRegCircle />}
              </div>
            }
          />
        </Link>
      )),
    [data],
  );

  return (
    <div>
      <h2 className="mb-3 border-b border-gray-300 pb-3 text-2xl font-semibold">
        <FormattedMessage id="global.issues" />
      </h2>
      {data?.length === 0 ? (
        <NoIssueFound />
      ) : (
        <QuerySwitcher
          skeletonClassname="h-[100px]"
          status={status}
          data={data}
        >
          {issueList}
        </QuerySwitcher>
      )}
    </div>
  );
};

export default IssueSection;
