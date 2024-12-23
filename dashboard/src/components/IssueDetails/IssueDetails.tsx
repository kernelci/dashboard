import { FormattedMessage, useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import type { ISection } from '@/components/Section/Section';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { getMiscSection } from '@/components/Section/MiscSection';

import { useIssueDetails } from '@/api/issueDetails';

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';

import { IssueDetailsTestSection } from './IssueDetailsTestSection';

interface IIssueDetails {
  issueId: string;
  versionNumber: string;
  tableFilter: TableFilter;
  onClickTestFilter: (filter: TestsTableFilter) => void;
  getTestTableRowLink: (testId: string) => LinkProps;
}

export const IssueDetails = ({
  issueId,
  versionNumber,
  tableFilter,
  onClickTestFilter,
  getTestTableRowLink,
}: IIssueDetails): JSX.Element => {
  const { data, error, isLoading } = useIssueDetails(issueId, versionNumber);

  const hasTest = data && data.test_status !== null;

  const { formatMessage } = useIntl();

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'globalDetails.miscData' }),
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
    return [...generalSections, miscSection].filter(
      section => section !== undefined,
    );
  }, [generalSections, miscSection]);

  if (error) {
    return (
      <div>
        <FormattedMessage id="issueDetails.failedToFetch" />
        <div>Error: {error.message}</div>
      </div>
    );
  }

  if (isLoading) return <FormattedMessage id="global.loading" />;

  if (!data) {
    return (
      <div>
        <FormattedMessage id="issueDetails.notFound" />
      </div>
    );
  }

  return (
    <ErrorBoundary FallbackComponent={UnexpectedError}>
      <SectionGroup sections={sectionsData} />
      {hasTest && (
        <IssueDetailsTestSection
          issueId={issueId}
          versionNumber={versionNumber}
          testTableFilter={tableFilter.testsTable}
          getTableRowLink={getTestTableRowLink}
          onClickFilter={onClickTestFilter}
        />
      )}
    </ErrorBoundary>
  );
};
