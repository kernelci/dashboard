import { memo, useCallback, useMemo, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem, { ItemType } from '@/components/ListingItem/ListingItem';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import type {
  RedirectFrom,
  TFilter,
  TFilterObjectsKeys,
} from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';

import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

import { UNCATEGORIZED_STRING } from '@/utils/constants/backend';

import { MemoizedMoreDetailsIconLink } from '@/components/Button/MoreDetailsButton';
import { IssueTooltip } from '@/components/Issue/IssueTooltip';

import { LinkIcon } from '@/components/Icons/Link';
import { getIssueFilterLabel } from '@/utils/utils';
import type { TIssue } from '@/types/issues';
import type { IssueExtraDetailsDict } from '@/types/issueExtras';

import { LoadingCircle } from '@/components/ui/loading-circle';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { BranchBadge } from '@/components/Badge/BranchBadge';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

interface IIssuesList {
  issues: TIssue[];
  failedWithUnknownIssues?: number;
  title: IBaseCard['title'];
  diffFilter: TFilter;
  issueFilterSection: TFilterObjectsKeys;
  detailsId?: string;
  pageFrom?: RedirectFrom;
  issueExtraDetails?: IssueExtraDetailsDict;
  extraDetailsLoading?: boolean; // TODO: make the isLoading not optional once applied to other pages
}

const IssuesList = ({
  issues,
  failedWithUnknownIssues,
  title,
  diffFilter,
  issueFilterSection,
  detailsId,
  pageFrom,
  issueExtraDetails,
  extraDetailsLoading,
}: IIssuesList): JSX.Element => {
  const getIssueLink = useCallback(
    (issueId: string, version: number): LinkProps => {
      return {
        to: '/issue/$issueId',
        params: {
          issueId: issueId,
        },
        search: s => ({
          origin: s.origin,
          issueVersion: version,
        }),
        state: s => ({ ...s, id: detailsId, from: pageFrom }),
      };
    },
    [detailsId, pageFrom],
  );

  const { formatMessage } = useIntl();

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

  const sortedIssues = useMemo(() => {
    if (!extraDetailsLoading && issueExtraDetails !== undefined) {
      const sortedIssueExtraDetails = Object.values(issueExtraDetails).sort(
        (a, b) =>
          new Date(b.first_incident.first_seen).getTime() -
          new Date(a.first_incident.first_seen).getTime(),
      );

      const issueIndexMap = new Map(
        sortedIssueExtraDetails.flatMap((obj, index) =>
          Object.values(obj.versions).map(version => [version.id, index]),
        ),
      );

      return issues.sort((a, b) => {
        const aIdx = issueIndexMap.get(a.id) ?? -1;
        const bIdx = issueIndexMap.get(b.id) ?? -1;
        return aIdx - bIdx;
      });
    }
    return issues;
  }, [extraDetailsLoading, issueExtraDetails, issues]);

  const contentElement = !hasIssue ? (
    <MemoizedSectionError
      isEmpty={true}
      isLoading={false}
      emptyLabel="issue.noIssueFound"
      variant="warning"
    />
  ) : (
    <DumbListingContent>
      {sortedIssues.map(issue => {
        const currentExtraDetailsId = issueExtraDetails?.[issue.id];
        const currentExtraDetailsVersion =
          currentExtraDetailsId?.['versions'][issue.version];

        const tagPills = currentExtraDetailsVersion?.tags?.map(tag => {
          return <BranchBadge key={tag} tag={tag} />;
        });

        if (
          detailsId === currentExtraDetailsId?.first_incident.git_commit_hash
        ) {
          tagPills?.unshift(
            <Tooltip>
              <TooltipTrigger className="cursor-default">
                <div className="starburst bg-red aspect-square w-[24px]"></div>
              </TooltipTrigger>
              <TooltipContent>
                <FormattedMessage id="issue.newIssue" />
              </TooltipContent>
            </Tooltip>,
          );
        }

        const first_seen = currentExtraDetailsId?.first_incident.first_seen;

        return (
          <div
            key={`${issue.id}${issue.version}`}
            className="flex w-full justify-between gap-4"
          >
            <div className="flex items-center gap-3">
              <div className="overflow-hidden">
                <FilterLink
                  filterSection={issueFilterSection}
                  filterValue={getIssueFilterLabel(issue)}
                  diffFilter={diffFilter}
                >
                  <span className="flex items-center text-sm">
                    <ListingItem
                      unknown={issue.incidents_info.incidentsCount}
                      hasBottomBorder
                      text={
                        issue.comment ??
                        formatMessage({ id: 'issue.uncategorized' })
                      }
                      tooltip={issue.comment}
                    />
                    {extraDetailsLoading ? (
                      <LoadingCircle className="mx-2" />
                    ) : (
                      first_seen && (
                        <span className="pb-1 text-nowrap text-gray-600">
                          <TooltipDateTime
                            dateTime={first_seen}
                            lineBreak={true}
                            showRelative={true}
                            message={`• ${formatMessage({ id: 'issue.firstSeen' })}: `}
                          />
                        </span>
                      )
                    )}
                  </span>
                </FilterLink>
              </div>
              {tagPills && !extraDetailsLoading && (
                <div className="flex gap-3">{...tagPills}</div>
              )}
            </div>
            <div className="flex items-center gap-4">
              {issue.report_url && (
                <LinkWithIcon
                  link={issue.report_url}
                  icon={<LinkIcon className="h-4 w-4" />}
                />
              )}
              {issue.id !== UNCATEGORIZED_STRING && (
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
          filterValue={UNCATEGORIZED_STRING}
          diffFilter={diffFilter}
        >
          <ListingItem
            unknown={failedWithUnknownIssues}
            text={formatMessage({ id: 'issue.uncategorized' })}
          />
        </FilterLink>
      )}
    </DumbListingContent>
  );

  return (
    <BaseCard
      title={titleElement}
      content={contentElement}
      className="col-span-2"
    />
  );
};

const MemoizedIssuesList = memo(IssuesList);

export default MemoizedIssuesList;
