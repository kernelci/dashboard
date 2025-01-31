import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo, useState } from 'react';

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

  const hasTest = data && data.test_status !== null;
  const hasBuild = data && data.build_valid !== null;
  const hasNothingIdentified = !hasTest && !hasBuild;

  const { formatMessage } = useIntl();

  const [jsonContent, setJsonContent] = useState<IJsonContent>();

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
        title: data.id,
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
                title: 'issueDetails.culpritCode',
                linkText: valueOrEmpty(data.culprit_code?.toString()),
              },
              {
                title: 'issueDetails.culpritTool',
                linkText: valueOrEmpty(data.culprit_tool?.toString()),
              },

              {
                title: 'issueDetails.culpritHarness',
                linkText: valueOrEmpty(data.culprit_harness?.toString()),
              },
              {
                title: 'issueDetails.buildValid',
                linkText: valueOrEmpty(data.build_valid?.toString()),
              },
              {
                title: 'globalTable.test',
                linkText: valueOrEmpty(data.test_status),
              },
              {
                title: 'issueDetails.comment',
                linkText: shouldTruncate(valueOrEmpty(data.comment)) ? (
                  <TruncatedValueTooltip value={data.comment} />
                ) : (
                  valueOrEmpty(data.comment)
                ),
              },
            ],
          },
        ],
      },
    ];
  }, [data, formatMessage]);

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
          {(hasTest || hasNothingIdentified) && (
            <IssueDetailsTestSection
              issueId={issueId}
              versionNumber={versionNumber}
              testTableFilter={tableFilter.testsTable}
              getTableRowLink={getTestTableRowLink}
              onClickFilter={onClickTestFilter}
            />
          )}
          {(hasBuild || hasNothingIdentified) && (
            <IssueDetailsBuildSection
              issueId={issueId}
              versionNumber={versionNumber}
              buildTableFilter={tableFilter.buildsTable}
              getTableRowLink={getBuildTableRowLink}
              onClickFilter={onClickBuildFilter}
            />
          )}
          <LogOrJsonSheetContent type="json" jsonContent={jsonContent} />
        </Sheet>
      </ErrorBoundary>
    </QuerySwitcher>
  );
};
