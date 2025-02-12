import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useCallback, useMemo, useState } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import type { ISection } from '@/components/Section/Section';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { getMiscSection } from '@/components/Section/MiscSection';

import { useIssueDetails } from '@/api/issueDetails';

import type {
  BuildsTableFilter,
  TableFilter,
  TestsTableFilter,
} from '@/types/tree/TreeDetails';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { Sheet } from '@/components/Sheet';
import {
  type IJsonContent,
  LogOrJsonSheetContent,
} from '@/components/Sheet/LogOrJsonSheetContent';

import { getLogspecSection } from '@/components/Section/LogspecSection';

import type { TIssueDetails } from '@/types/issueDetails';

import { IssueDetailsTestSection } from './IssueDetailsTestSection';

import { IssueDetailsBuildSection } from './IssueDetailsBuildSection';

interface IIssueDetails {
  issueId: string;
  versionNumber?: number;
  tableFilter: TableFilter;
  onClickTestFilter: (filter: TestsTableFilter) => void;
  getTestTableRowLink: (testId: string) => LinkProps;
  onClickBuildFilter: (filter: BuildsTableFilter) => void;
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

  const generalSections: ISection[] = useMemo(() => {
    if (!data) {
      return [];
    }
    return [
      {
        title: data.comment ?? data.id,
        eyebrow: formatMessage({ id: 'issueDetails.issueDetails' }),
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
  }, [data, formatMessage, getCulpritValue]);

  const sectionsData: ISection[] = useMemo(() => {
    return [...generalSections, logspecSection, miscSection].filter(
      section => section !== undefined,
    );
  }, [generalSections, logspecSection, miscSection]);

  return (
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
  );
};
