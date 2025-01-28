import { memo, useCallback } from 'react';

import { useIntl } from 'react-intl';

import { MdLink } from 'react-icons/md';

import type { LinkProps } from '@tanstack/react-router';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem, { ItemType } from '@/components/ListingItem/ListingItem';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { NoIssueFound } from '@/components/Issue/IssueSection';
import type {
  RedirectFrom,
  TFilter,
  TFilterObjectsKeys,
  TIssue,
} from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';

import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

import { UNKNOWN_STRING } from '@/utils/constants/backend';

import { MemoizedMoreDetailsIconLink } from '@/components/Button/MoreDetailsButton';
import { IssueTooltip } from '@/components/Issue/IssueTooltip';

interface IIssuesList {
  issues: TIssue[];
  failedWithUnknownIssues?: number;
  title: IBaseCard['title'];
  diffFilter: TFilter;
  issueFilterSection: TFilterObjectsKeys;
  detailsId?: string;
  pageFrom?: RedirectFrom;
}

const IssuesList = ({
  issues,
  failedWithUnknownIssues,
  title,
  diffFilter,
  issueFilterSection,
  detailsId,
  pageFrom,
}: IIssuesList): JSX.Element => {
  const getIssueLink = useCallback(
    (issueId: string, version: string): LinkProps => ({
      to: '/issue/$issueId/version/$versionNumber',
      params: {
        issueId: issueId,
        versionNumber: version,
      },
      search: s => s,
      state: { id: detailsId, from: pageFrom },
    }),
    [detailsId, pageFrom],
  );

  const intl = useIntl();

  failedWithUnknownIssues = failedWithUnknownIssues
    ? failedWithUnknownIssues
    : undefined;
  const hasIssue = issues.length > 0 || failedWithUnknownIssues;

  const titleElement = (
    <div className="flex items-center gap-4 pr-4">
      <span>
        {title}
        {hasIssue && (
          <ColoredCircle
            className="ml-2 font-normal"
            backgroundClassName={ItemType.Error}
            quantity={issues.length + (failedWithUnknownIssues ? 1 : 0)}
          />
        )}
      </span>
      <IssueTooltip />
    </div>
  );

  const contentElement = !hasIssue ? (
    <NoIssueFound />
  ) : (
    <DumbListingContent>
      {issues.map(issue => {
        return (
          <div key={issue.id} className="flex w-full justify-between gap-4">
            <div className="overflow-hidden">
              <FilterLink
                filterSection={issueFilterSection}
                filterValue={issue.id}
                diffFilter={diffFilter}
              >
                <ListingItem
                  unknown={issue.incidents_info.incidentsCount}
                  hasBottomBorder
                  text={
                    issue.comment ??
                    intl.formatMessage({ id: 'global.unknown' })
                  }
                  tooltip={issue.comment}
                />
              </FilterLink>
            </div>
            <div className="flex items-center gap-4">
              {issue.report_url && (
                <LinkWithIcon
                  link={issue.report_url}
                  icon={<MdLink className="h-4 w-4" />}
                />
              )}
              {issue.id !== UNKNOWN_STRING && (
                <MemoizedMoreDetailsIconLink
                  linkProps={getIssueLink(issue.id, issue.version)}
                />
              )}
            </div>
          </div>
        );
      })}
      {failedWithUnknownIssues && (
        <FilterLink
          filterSection={issueFilterSection}
          filterValue={'Unknown'}
          diffFilter={diffFilter}
        >
          <ListingItem
            unknown={failedWithUnknownIssues}
            text={intl.formatMessage({ id: 'global.unknown' })}
          />
        </FilterLink>
      )}
    </DumbListingContent>
  );

  return <BaseCard title={titleElement} content={contentElement} />;
};

const MemoizedIssuesList = memo(IssuesList);

export default MemoizedIssuesList;
