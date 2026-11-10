import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo, useState, type JSX } from 'react';

import { useParams, type LinkProps } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import Section, {
  type ISection,
  type SubsectionLink,
} from '@/components/Section/Section';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { valueOrEmpty } from '@/lib/string';

import { getMiscSection } from '@/components/Section/MiscSection';

import { useIssueDetails } from '@/api/issueDetails';

import type { TableFilter, TableStatusOption } from '@/types/tree/TreeDetails';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { Sheet } from '@/components/Sheet';
import {
  type IJsonContent,
  LogOrJsonSheetContent,
} from '@/components/Sheet/LogOrJsonSheetContent';

import { BranchBadge } from '@/components/Badge/BranchBadge';

import { getLogspecSection } from '@/components/Section/LogspecSection';

import PageWithTitle from '@/components/PageWithTitle';

import { getTitle } from '@/utils/utils';

import { getIssueCulprit } from '@/lib/issue';

import { MemoizedIssueDetailsOGTags } from '@/components/OpenGraphTags/IssueDetailsOGTags';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

import { Badge } from '@/components/ui/badge';

import { MemoizedKcidevCommandButton } from '@/components/Footer/KcidevCommandButton';
import { createIssueDetailsCommand } from '@/components/Footer/kcidevCommand';

import { DetailsInfoCard } from '@/components/Cards/DetailsInfoCard';

import { IncidentsSection } from './IncidentsSection';

import { IssueDetailsTestSection } from './IssueDetailsTestSection';

import { IssueDetailsBuildSection } from './IssueDetailsBuildSection';

interface IIssueDetails {
  versionNumber?: number;
  tableFilter: TableFilter;
  onToggleTestFilter: (option: TableStatusOption) => void;
  getTestTableRowLink: (testId: string) => LinkProps;
  onToggleBuildFilter: (option: TableStatusOption) => void;
  getBuildTableRowLink: (testId: string) => LinkProps;
  breadcrumb?: JSX.Element;
}

export const IssueDetails = ({
  versionNumber,
  tableFilter,
  onToggleTestFilter,
  getTestTableRowLink,
  onToggleBuildFilter,
  getBuildTableRowLink,
  breadcrumb,
}: IIssueDetails): JSX.Element => {
  const { issueId } = useParams({ from: '/_main/issue/$issueId' });
  const { data, isLoading, status, error } = useIssueDetails(
    issueId,
    versionNumber,
  );

  const { formatMessage } = useIntl();

  const [jsonContent, setJsonContent] = useState<IJsonContent>();

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'commonDetails.miscData' }),
    });
  }, [data?.misc, formatMessage]);

  const logspecSection: ISection | undefined = useMemo(() => {
    return getLogspecSection({
      misc: data?.misc,
      title: formatMessage({ id: 'issueDetails.logspecData' }),
      parserTitle: formatMessage({ id: 'logspec.parser' }),
      setJsonContent: setJsonContent,
    });
  }, [data?.misc, formatMessage]);

  const tagPills = useMemo(() => {
    const branchTags: JSX.Element[] = [];
    const categoryTags: JSX.Element[] = [];

    if (data?.extra?.[issueId]?.versions !== undefined) {
      Object.values(data.extra[issueId].versions)[0].tags?.map(tag =>
        branchTags.push(<BranchBadge key={tag} tag={tag} />),
      );
    }

    if (data?.categories) {
      data.categories.map(category =>
        categoryTags.push(
          <Badge key={category} variant={'blueTag'} className="my-0.5">
            {category}
          </Badge>,
        ),
      );
    }

    const hasBranchTags = branchTags.length > 0;
    const hasCategoryTags = categoryTags.length > 0;

    if (hasBranchTags || hasCategoryTags) {
      return (
        <div className="flex gap-3">
          {hasBranchTags && <div className="flex gap-2">{...branchTags}</div>}
          {hasBranchTags && hasCategoryTags && (
            <span className="text-dark-gray2">|</span>
          )}
          {hasCategoryTags && (
            <div className="flex gap-2">{...categoryTags}</div>
          )}
        </div>
      );
    }
  }, [data, issueId]);

  const issueCulprit = useMemo(() => {
    return getIssueCulprit({
      culprit_code: data?.culprit_code,
      culprit_harness: data?.culprit_harness,
      culprit_tool: data?.culprit_tool,
      formatMessage: formatMessage,
    });
  }, [
    data?.culprit_code,
    data?.culprit_harness,
    data?.culprit_tool,
    formatMessage,
  ]);

  const issueInfo = useMemo((): SubsectionLink[] | undefined => {
    if (!data) {
      return;
    }

    const reportUrl = valueOrEmpty(data.report_url);
    const loreUrl = `https://lore.kernel.org/all/?q=${encodeURIComponent(data.id)}`;
    const reportSubject = valueOrEmpty(data.report_subject);

    return [
      {
        title: 'issueDetails.version',
        linkText: data.version.toString(),
      },
      {
        title: 'global.origin',
        linkText: valueOrEmpty(data.origin),
      },
      {
        title: 'issueDetails.loreUrl',
        linkText: loreUrl,
        link: loreUrl,
        span: 4,
      },
      ...(data.regzbot_url
        ? [
            {
              title: 'issueDetails.regzbotUrl',
              linkText: data.regzbot_url,
              link: data.regzbot_url,
              span: 4,
            } satisfies SubsectionLink,
          ]
        : []),
      {
        title: 'issueDetails.reportUrl',
        linkText: reportUrl,
        link: data.report_url ?? undefined,
        span: 4,
      },
      {
        title: 'issueDetails.reportSubject',
        linkText: reportSubject,
        span: 4,
      },
      {
        title: 'issueDetails.culpritTitle',
        linkText: issueCulprit,
        titleIcon: <TooltipIcon tooltipId="issueListing.culpritInfo" />,
      },
      {
        title: 'issueDetails.id',
        linkText: valueOrEmpty(data.id),
        span: 3,
      },
    ];
  }, [data, issueCulprit]);

  const generalSections: ISection[] = useMemo(() => {
    if (!data) {
      return [];
    }

    return [
      {
        title: data.comment ?? data.id,
        subtitle: tagPills,
        actions: (
          <MemoizedKcidevCommandButton
            command={createIssueDetailsCommand({
              id: issueId,
              origin: data.origin,
              omittedFilters:
                versionNumber === undefined ? [] : ['issue version'],
            })}
          />
        ),
      },
    ];
  }, [data, issueId, tagPills, versionNumber]);

  const issueDetailsTabTitle = useMemo(() => {
    return formatMessage(
      { id: 'title.issueDetails' },
      { issueName: getTitle(data?.comment, isLoading) },
    );
  }, [data?.comment, formatMessage, isLoading]);

  return (
    <PageWithTitle title={issueDetailsTabTitle}>
      <MemoizedIssueDetailsOGTags
        title={issueDetailsTabTitle}
        issueCulprit={issueCulprit}
        issueId={issueId}
        data={data}
      />
      <QuerySwitcher
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="issueDetails.notFound"
          />
        }
      >
        <ErrorBoundary FallbackComponent={UnexpectedError}>
          <Sheet>
            <div className="flex flex-col gap-6 pb-10">
              {breadcrumb}
              <SectionGroup sections={generalSections} />
              <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-2">
                <div className="flex flex-col gap-4">
                  {issueInfo && (
                    <DetailsInfoCard
                      cardTitle="issueDetails.issueInfo"
                      data={issueInfo}
                    />
                  )}
                  <IncidentsSection
                    firstIncident={data?.extra?.[issueId]?.first_incident}
                    lastIncident={data?.extra?.[issueId]?.last_incident}
                    nextCheckout={data?.extra?.[issueId]?.next_checkout}
                    perTree={data?.extra?.[issueId]?.per_tree}
                  />
                  {miscSection && <Section {...miscSection} card />}
                </div>
                <div className="flex flex-col gap-4">
                  {logspecSection && <Section {...logspecSection} card />}
                </div>
              </div>
              <IssueDetailsTestSection
                issueId={issueId}
                versionNumber={versionNumber}
                testTableFilter={tableFilter.testsTable}
                getTableRowLink={getTestTableRowLink}
                onToggleFilter={onToggleTestFilter}
              />
              <IssueDetailsBuildSection
                issueId={issueId}
                versionNumber={versionNumber}
                buildTableFilter={tableFilter.buildsTable}
                getTableRowLink={getBuildTableRowLink}
                onToggleFilter={onToggleBuildFilter}
              />
              <LogOrJsonSheetContent type="json" jsonContent={jsonContent} />
            </div>
          </Sheet>
        </ErrorBoundary>
      </QuerySwitcher>
    </PageWithTitle>
  );
};
