import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useCallback, useMemo, useState, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';

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

import type { TIssueDetails } from '@/types/issueDetails';

import PageWithTitle from '@/components/PageWithTitle';

import { getTitle } from '@/utils/utils';

import { IssueDetailsTestSection } from './IssueDetailsTestSection';

import { IssueDetailsBuildSection } from './IssueDetailsBuildSection';

interface IIssueDetails {
  issueId: string;
  versionNumber?: number;
  tableFilter: TableFilter;
  onClickTestFilter: (filter: PossibleTableFilters) => void;
  getTestTableRowLink: (testId: string) => LinkProps;
  onClickBuildFilter: (filter: PossibleTableFilters) => void;
  getBuildTableRowLink: (testId: string) => LinkProps;
  breadcrumb?: JSX.Element;
}

type CulpritIssue = Pick<
  TIssueDetails,
  'culprit_code' | 'culprit_harness' | 'culprit_tool'
>;

export const IssueDetails = ({
  issueId,
  versionNumber,
  tableFilter,
  onClickTestFilter,
  getTestTableRowLink,
  onClickBuildFilter,
  getBuildTableRowLink,
  breadcrumb,
}: IIssueDetails): JSX.Element => {
  const { data, isLoading, status, error } = useIssueDetails(
    issueId,
    versionNumber,
  );

  const { formatMessage } = useIntl();

  const [jsonContent, setJsonContent] = useState<IJsonContent>();

  const getCulpritValue = useCallback(
    ({ culprit_code, culprit_harness, culprit_tool }: CulpritIssue): string => {
      const result: string[] = [];

      if (culprit_code) {
        result.push(formatMessage({ id: 'issueDetails.culpritCode' }));
      }
      if (culprit_harness) {
        result.push(formatMessage({ id: 'issueDetails.culpritHarness' }));
      }
      if (culprit_tool) {
        result.push(formatMessage({ id: 'issueDetails.culpritTool' }));
      }

      return valueOrEmpty(result.join(', '));
    },
    [formatMessage],
  );

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'globalDetails.miscData' }),
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
    if (data?.extra?.[issueId]?.versions !== undefined) {
      return (
        <div className="flex gap-3">
          {Object.values(data.extra[issueId].versions)[0].tags?.map(tag => (
            <BranchBadge key={tag} tag={tag} />
          ))}
        </div>
      );
    }
  }, [data, issueId]);

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
                linkText: getCulpritValue(data),
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
  }, [data, tagPills, formatMessage, getCulpritValue]);

  const sectionsData: ISection[] = useMemo(() => {
    return [
      ...generalSections,
      firstIncidentSection,
      logspecSection,
      miscSection,
    ].filter(section => !!section);
  }, [generalSections, logspecSection, miscSection, firstIncidentSection]);

  return (
    <PageWithTitle
      title={formatMessage(
        { id: 'title.issueDetails' },
        { issueName: getTitle(data?.comment, isLoading) },
      )}
    >
      <QuerySwitcher
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel={'global.error'}
          />
        }
      >
        <ErrorBoundary FallbackComponent={UnexpectedError}>
          <Sheet>
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
          </Sheet>
        </ErrorBoundary>
      </QuerySwitcher>
    </PageWithTitle>
  );
};
