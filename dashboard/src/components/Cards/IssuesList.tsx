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

import { GroupedTestStatus } from '@/components/Status/Status';

type IssueItemProps = {
  issue: TIssue;
  extraDetails?: IssueExtraDetailsDict[string];
  extraDetailsLoading?: boolean;
  detailsId?: string;
  getIssueLink: (id: string, version: number) => LinkProps;
  issueFilterSection: TFilterObjectsKeys;
  diffFilter: TFilter;
};

const IssueItem = ({
  issue,
  extraDetails,
  extraDetailsLoading,
  detailsId,
  getIssueLink,
  issueFilterSection,
  diffFilter,
}: IssueItemProps): JSX.Element => {
  const { formatMessage } = useIntl();

  const isFirstIncident =
    detailsId === extraDetails?.first_incident.git_commit_hash;
  const currentVersion = extraDetails?.versions[issue.version];
  const firstSeen = extraDetails?.first_incident.first_seen;
  const counts = issue.incidents_info;

  const tagPills = currentVersion?.tags?.map(tag => (
    <BranchBadge key={tag} tag={tag} />
  ));

  if (isFirstIncident) {
    tagPills?.unshift(
      <Tooltip key="starburst">
        <TooltipTrigger className="cursor-default">
          <div className="starburst bg-red aspect-square w-[24px]" />
        </TooltipTrigger>
        <TooltipContent>
          <FormattedMessage id="issue.newIssue" />
        </TooltipContent>
      </Tooltip>,
    );
  }

  const hasMeta = !extraDetailsLoading && !!(firstSeen || tagPills?.length);

  return (
    <div className="grid w-full grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-3">
      {/* Col 1: status circles — fixed width */}
      <GroupedTestStatus
        pass={counts.PASS}
        fail={counts.FAIL}
        nullStatus={counts.NULL}
        error={counts.ERROR}
        done={counts.DONE}
        miss={counts.MISS}
        skip={counts.SKIP}
      />

      {/* Col 2: issue text — takes remaining space, truncates */}
      <FilterLink
        filterSection={issueFilterSection}
        filterValue={getIssueFilterLabel(issue)}
        diffFilter={diffFilter}
      >
        <div className="max-w-5/6 min-w-0 text-sm sm:max-w-3/4">
          <ListingItem
            showNumber={false}
            hasBottomBorder
            text={issue.comment ?? formatMessage({ id: 'issue.uncategorized' })}
            tooltip={issue.comment}
          />
        </div>
      </FilterLink>

      {/* Col 3: action icons — fixed width */}
      <div className="flex items-center gap-3">
        {extraDetailsLoading && <LoadingCircle />}
        {!extraDetailsLoading && issue.report_url && (
          <LinkWithIcon
            link={issue.report_url}
            icon={<LinkIcon className="h-4 w-4" />}
          />
        )}
        {!extraDetailsLoading && issue.id !== UNCATEGORIZED_STRING && (
          <MemoizedMoreDetailsIconLink
            linkProps={getIssueLink(issue.id, issue.version)}
          />
        )}
      </div>

      {/* Row 2, Col 2: first_seen + tags below text, col 1 and 3 stay empty */}
      {hasMeta && (
        <div className="col-start-2 flex flex-wrap items-center gap-2 pb-1">
          {firstSeen && (
            <span className="text-sm text-nowrap text-gray-600">
              <TooltipDateTime
                dateTime={firstSeen}
                lineBreak={true}
                showRelative={true}
                message={`• ${formatMessage({ id: 'issue.firstSeen' })}: `}
              />
            </span>
          )}
          {tagPills && (
            <div className="flex flex-wrap gap-2">{...tagPills}</div>
          )}
        </div>
      )}
    </div>
  );
};

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
      {sortedIssues.map(issue => (
        <IssueItem
          key={`${issue.id}${issue.version}`}
          issue={issue}
          extraDetails={issueExtraDetails?.[issue.id]}
          extraDetailsLoading={extraDetailsLoading}
          detailsId={detailsId}
          getIssueLink={getIssueLink}
          issueFilterSection={issueFilterSection}
          diffFilter={diffFilter}
        />
      ))}
      {failedWithUnknownIssues && (
        <FilterLink
          filterSection={issueFilterSection}
          filterValue={UNCATEGORIZED_STRING}
          diffFilter={diffFilter}
        >
          <ListingItem
            errors={failedWithUnknownIssues}
            text={formatMessage({ id: 'issue.uncategorized' })}
          />
        </FilterLink>
      )}
    </DumbListingContent>
  );

  return <BaseCard title={titleElement} content={contentElement} />;
};

const MemoizedIssuesList = memo(IssuesList);

export default MemoizedIssuesList;
