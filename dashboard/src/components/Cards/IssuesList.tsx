import { memo } from 'react';

import { useIntl } from 'react-intl';

import { MdLink } from 'react-icons/md';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem, { ItemType } from '@/components/ListingItem/ListingItem';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { NoIssueFound } from '@/components/Issue/IssueSection';
import type { TFilter, TFilterObjectsKeys, TIssue } from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';

import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

interface IIssuesList {
  issues: TIssue[];
  failedWithUnknownIssues?: number;
  title: IBaseCard['title'];
  diffFilter: TFilter;
  issueFilterSection: TFilterObjectsKeys;
}

const IssuesList = ({
  issues,
  failedWithUnknownIssues,
  title,
  diffFilter,
  issueFilterSection,
}: IIssuesList): JSX.Element => {
  const intl = useIntl();
  failedWithUnknownIssues = failedWithUnknownIssues
    ? failedWithUnknownIssues
    : undefined;
  const hasIssue = issues.length > 0 || failedWithUnknownIssues;

  const titleElement = (
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
  );

  const contentElement = !hasIssue ? (
    <NoIssueFound />
  ) : (
    <DumbListingContent>
      {issues.map(issue => {
        return (
          <div key={issue.id} className="flex w-full items-center">
            {issue.report_url && (
              <div className="pb-1 pr-2">
                <LinkWithIcon
                  link={issue.report_url}
                  icon={<MdLink className="h-4 w-4" />}
                />
              </div>
            )}
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
