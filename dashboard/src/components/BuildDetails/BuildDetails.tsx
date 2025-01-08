import { ImTree } from 'react-icons/im';

import { MdClose, MdCheck, MdFolderOpen } from 'react-icons/md';

import { FormattedMessage, useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo } from 'react';

import {
  useSearch,
  type HistoryState,
  type LinkProps,
} from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import type { ISection } from '@/components/Section/Section';
import { useBuildDetails, useBuildIssues } from '@/api/buildDetails';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { formatDate } from '@/utils/utils';

import IssueSection from '@/components/Issue/IssueSection';

import { valueOrEmpty } from '@/lib/string';

import { Sheet, SheetTrigger } from '@/components/Sheet';

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';

import { LogSheetContent } from '@/components/Log/LogSheetContent';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { getMiscSection } from '@/components/Section/MiscSection';

import { getFilesSection } from '@/components/Section/FilesSection';

import BuildDetailsTestSection from './BuildDetailsTestSection';

const BlueFolderIcon = (): JSX.Element => (
  <MdFolderOpen className="text-blue" />
);

interface BuildDetailsProps {
  breadcrumb?: JSX.Element;
  buildId?: string;
  onClickFilter: (filter: TestsTableFilter) => void;
  tableFilter: TableFilter;
  getTestTableRowLink: (testId: string) => LinkProps;
  historyState?: HistoryState;
}

const BuildDetails = ({
  breadcrumb,
  buildId,
  onClickFilter,
  tableFilter,
  getTestTableRowLink,
  historyState,
}: BuildDetailsProps): JSX.Element => {
  const searchParams = useSearch({ from: '/build/$buildId' });
  const { data, error, isLoading } = useBuildDetails(buildId ?? '');
  const { data: issueData, status: issueStatus } = useBuildIssues(
    buildId ?? '',
  );

  const { formatMessage } = useIntl();

  const hasUsefulLogInfo = data?.log_url || data?.log_excerpt;

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'globalDetails.miscData' }),
    });
  }, [data?.misc, formatMessage]);

  const filesSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getFilesSection({
      inputFiles: data?.input_files,
      outputFiles: data?.output_files,
      title: formatMessage({ id: 'globalDetails.artifacts' }),
    });
  }, [data?.input_files, data?.output_files, formatMessage]);

  const generalSections: ISection[] = useMemo(() => {
    if (!data) {
      return [];
    }
    return [
      {
        title: valueOrEmpty(
          data.git_commit_name
            ? `${data.git_commit_name} • ${data.config_name}`
            : data.config_name,
        ),
        eyebrow: formatMessage({ id: 'buildDetails.buildDetails' }),
        subsections: [
          {
            infos: [
              {
                title: 'global.tree',
                linkText: valueOrEmpty(data.tree_name),
                icon: <ImTree className="text-blue" />,
              },
              {
                title: 'buildDetails.gitUrl',
                linkText: (
                  <TruncatedValueTooltip
                    value={data.git_repository_url}
                    isUrl={true}
                  />
                ),
                link: data.git_repository_url,
              },
              {
                title: 'buildDetails.gitBranch',
                linkText: valueOrEmpty(data.git_repository_branch),
                icon: <ImTree className="text-blue" />,
              },
              {
                title: 'buildDetails.gitCommit',
                linkText: valueOrEmpty(data.git_commit_hash),
              },
              {
                title: 'buildDetails.gitDescribe',
                linkText: valueOrEmpty(data.git_commit_name),
              },
              {
                title: 'global.date',
                linkText: formatDate(valueOrEmpty(data.start_time)),
              },
              {
                title: 'buildDetails.defconfig',
                linkText: valueOrEmpty(data.config_name),
              },
              {
                title: 'global.status',
                icon: data.valid ? (
                  <MdCheck className="text-green" />
                ) : (
                  <MdClose className="text-red" />
                ),
              },
              {
                title: 'global.architecture',
                linkText: valueOrEmpty(data.architecture),
              },
              {
                title: 'buildDetails.buildTime',
                linkText: data.duration ? `${data.duration} sec` : '-',
              },
              {
                title: 'buildDetails.compiler',
                linkText: valueOrEmpty(data.compiler),
              },
              {
                title: 'global.command',
                linkText: valueOrEmpty(data.command),
              },
            ],
          },
          {
            infos: [
              {
                title: 'buildDetails.buildLogs',
                linkText: (
                  <TruncatedValueTooltip value={data.log_url} isUrl={true} />
                ),
                icon: hasUsefulLogInfo ? <BlueFolderIcon /> : undefined,
                wrapperComponent: hasUsefulLogInfo ? SheetTrigger : undefined,
              },
              {
                title: 'buildDetails.kernelConfig',
                linkText: (
                  <TruncatedValueTooltip value={data.config_url} isUrl={true} />
                ),
                link: data.config_url,
              },
            ],
          },
        ],
      },
    ];
  }, [data, formatMessage, hasUsefulLogInfo]);

  const sectionsData: ISection[] = useMemo(() => {
    return [...generalSections, miscSection, filesSection].filter(
      section => section !== undefined,
    );
  }, [generalSections, miscSection, filesSection]);

  if (error) {
    return (
      <div>
        <FormattedMessage id="buildDetails.failedToFetch" />
      </div>
    );
  }

  if (isLoading) return <FormattedMessage id="global.loading" />;

  if (!data) {
    return (
      <div>
        <FormattedMessage id="buildDetails.notFound" />
      </div>
    );
  }

  return (
    <ErrorBoundary FallbackComponent={UnexpectedError}>
      <Sheet>
        {breadcrumb}

        <SectionGroup sections={sectionsData} />
        <BuildDetailsTestSection
          buildId={buildId ?? ''}
          onClickFilter={onClickFilter}
          tableFilter={tableFilter}
          getRowLink={getTestTableRowLink}
        />
        <IssueSection
          data={issueData}
          status={issueStatus}
          historyState={historyState}
          previousSearch={searchParams}
        />
        <LogSheetContent logUrl={data.log_url} logExcerpt={data.log_excerpt} />
      </Sheet>
    </ErrorBoundary>
  );
};

export default BuildDetails;
