import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo, useState, type JSX } from 'react';

import { useParams, type LinkProps } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import type { ISection } from '@/components/Section/Section';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { getMiscSection } from '@/components/Section/MiscSection';

import { useIssueDetails } from '@/api/issueDetails';

import type {
  TableFilter,
  PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { Sheet } from '@/components/Sheet';
import {
  type IJsonContent,
  LogOrJsonSheetContent,
} from '@/components/Sheet/LogOrJsonSheetContent';

import { BranchBadge } from '@/components/Badge/BranchBadge';

import { getLogspecSection } from '@/components/Section/LogspecSection';
import { getFirstIncidentSection } from '@/components/Section/FirstIncidentSection';

import PageWithTitle from '@/components/PageWithTitle';

import { getTitle } from '@/utils/utils';

import { getIssueCulprit } from '@/lib/issue';

import { MemoizedIssueDetailsOGTags } from '@/components/OpenGraphTags/IssueDetailsOGTags';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

import { Badge } from '@/components/ui/badge';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { IssueDetailsTestSection } from './IssueDetailsTestSection';

import { IssueDetailsBuildSection } from './IssueDetailsBuildSection';

interface IIssueDetails {
  versionNumber?: number;
  tableFilter: TableFilter;
  onClickTestFilter: (filter: PossibleTableFilters) => void;
  getTestTableRowLink: (testId: string) => LinkProps;
  onClickBuildFilter: (filter: PossibleTableFilters) => void;
  getBuildTableRowLink: (testId: string) => LinkProps;
  breadcrumb?: JSX.Element;
}

export const IssueDetails = ({
  versionNumber,
  tableFilter,
  onClickTestFilter,
  getTestTableRowLink,
  onClickBuildFilter,
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
      setJsonContent: setJsonContent,
    });
  }, [data?.misc, formatMessage]);

  const logspecSection: ISection | undefined = useMemo(() => {
    return getLogspecSection({
      misc: data?.misc,
      title: formatMessage({ id: 'issueDetails.logspecData' }),
      setJsonContent: setJsonContent,
    });
  }, [data?.misc, formatMessage]);

  const firstIncidentSection: ISection | undefined = useMemo(() => {
    return getFirstIncidentSection({
      firstIncident: data?.extra?.[issueId]?.first_incident,
      title: formatMessage({ id: 'issueDetails.firstIncidentData' }),
    });
  }, [data?.extra, formatMessage, issueId]);

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

  const generalSections: ISection[] = useMemo(() => {
    if (!data) {
      return [];
    }
    return [
      {
        title: data.comment ?? data.id,
        eyebrow: formatMessage({ id: 'issueDetails.issueDetails' }),
        subtitle: tagPills,
        subsections: [
          {
            infos: [
              {
                title: 'issueDetails.version',
                linkText: data.version.toString(),
              },
              {
                title: 'global.origin',
                linkText: valueOrEmpty(data.origin),
              },
              {
                title: 'issueDetails.reportUrl',
                linkText: shouldTruncate(valueOrEmpty(data.report_url)) ? (
                  <TruncatedValueTooltip value={data.report_url} isUrl={true} />
                ) : (
                  valueOrEmpty(data.report_url)
                ),
                link: data.report_url ?? undefined,
              },
              {
                title: 'issueDetails.reportSubject',
                linkText: shouldTruncate(valueOrEmpty(data.report_subject)) ? (
                  <TruncatedValueTooltip value={data.report_subject} />
                ) : (
                  valueOrEmpty(data.report_subject)
                ),
              },
              {
                title: 'issueDetails.culpritTitle',
                linkText: issueCulprit,
                titleIcon: <TooltipIcon tooltipId="issueListing.culpritInfo" />,
              },
              {
                title: 'issueDetails.id',
                linkText: shouldTruncate(valueOrEmpty(data.id)) ? (
                  <TruncatedValueTooltip value={data.id} />
                ) : (
                  data.id
                ),
              },
            ],
          },
        ],
      },
    ];
  }, [data, tagPills, formatMessage, issueCulprit]);

  const sectionsData: ISection[] = useMemo(() => {
    return [
      ...generalSections,
      firstIncidentSection,
      logspecSection,
      miscSection,
    ].filter(section => !!section);
  }, [generalSections, logspecSection, miscSection, firstIncidentSection]);

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
            <div className="pb-10">
              {breadcrumb}
              <SectionGroup sections={sectionsData} />
              <IssueDetailsTestSection
                issueId={issueId}
                versionNumber={versionNumber}
                testTableFilter={tableFilter.testsTable}
                getTableRowLink={getTestTableRowLink}
                onClickFilter={onClickTestFilter}
              />
              <IssueDetailsBuildSection
                issueId={issueId}
                versionNumber={versionNumber}
                buildTableFilter={tableFilter.buildsTable}
                getTableRowLink={getBuildTableRowLink}
                onClickFilter={onClickBuildFilter}
              />
              <LogOrJsonSheetContent type="json" jsonContent={jsonContent} />
              <MemoizedKcidevFooter commandGroup="issue" />
            </div>
          </Sheet>
        </ErrorBoundary>
      </QuerySwitcher>
    </PageWithTitle>
  );
};
