import { memo } from 'react';

import { Link } from '@tanstack/react-router';

import { useIntl } from 'react-intl';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem, { ItemType } from '@/components/ListingItem/ListingItem';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { NoIssueFound } from '@/components/Issue/IssueSection';
import type { TIssue } from '@/types/general';

interface IIssuesList {
  issues: TIssue[];
  failedWithUnknownIssues?: number;
  title: IBaseCard['title'];
}

const IssuesList = ({
  issues,
  failedWithUnknownIssues,
  title,
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
        const WrapperLink = issue.report_url ? Link : 'div';
        return (
          <WrapperLink key={issue.id} to={issue.report_url} target="_blank">
            <ListingItem
              unknown={issue.incidents_info.incidentsCount}
              hasBottomBorder
              text={issue.comment ?? ''}
              tooltip={issue.comment}
            />
          </WrapperLink>
        );
      })}
      {failedWithUnknownIssues && (
        <ListingItem
          unknown={failedWithUnknownIssues}
          text={intl.formatMessage({ id: 'global.unknown' })}
        />
      )}
    </DumbListingContent>
  );

  return <BaseCard title={titleElement} content={contentElement} />;
};

export default memo(IssuesList);
