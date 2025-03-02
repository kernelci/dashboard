import { useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useCallback, useMemo, useState, type JSX } from 'react';

import {
  useNavigate,
  useParams,
  useSearch,
  type LinkProps,
} from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import type { ISection } from '@/components/Section/Section';
import { useBuildDetails, useBuildIssues } from '@/api/buildDetails';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { formatDate, getBuildStatus, getTitle } from '@/utils/utils';

import IssueSection from '@/components/Issue/IssueSection';

import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import { Sheet } from '@/components/Sheet';

import type {
  TableFilter,
  PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { getMiscSection } from '@/components/Section/MiscSection';

import { getFilesSection } from '@/components/Section/FilesSection';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { StatusIcon } from '@/components/Icons/StatusIcons';

import PageWithTitle from '@/components/PageWithTitle';

import { MemoizedBuildDetailsOGTags } from '@/components/OpenGraphTags/BuildDetailsOGTags';
import ButtonOpenLogSheet from '@/components/Button/ButtonOpenLogSheet';

import BuildDetailsTestSection from './BuildDetailsTestSection';

interface BuildDetailsProps {
  breadcrumb?: JSX.Element;
  onClickFilter: (filter: PossibleTableFilters) => void;
  tableFilter: TableFilter;
  getTestTableRowLink: (testId: string) => LinkProps;
}

const BuildDetails = ({
  breadcrumb,
  onClickFilter,
  tableFilter,
  getTestTableRowLink,
}: BuildDetailsProps): JSX.Element => {
  const { buildId } = useParams({ from: '/_main/build/$buildId' });
  const { data, isLoading, status, error } = useBuildDetails(buildId);
  const {
    data: issueData,
    status: issueStatus,
    error: issueError,
  } = useBuildIssues(buildId);

  const { logOpen } = useSearch({ from: '/_main/build/$buildId' });
  const navigate = useNavigate({ from: '/build/$buildId' });
  const { formatMessage } = useIntl();

  const [sheetType, setSheetType] = useState<SheetType>('log');
  const [jsonContent, setJsonContent] = useState<IJsonContent>();
  const logOpenChange = useCallback(
    (isOpen: boolean) =>
      navigate({ search: s => ({ ...s, logOpen: isOpen }), state: s => s }),
    [navigate],
  );

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'globalDetails.miscData' }),
      setSheetType: setSheetType,
      setJsonContent: setJsonContent,
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

  const setSheetToLog = useCallback(
    (): void => setSheetType('log'),
    [setSheetType],
  );

  const buildDetailsTitle: string = useMemo(() => {
    if (data?.git_commit_name && data.config_name) {
      return `${data.git_commit_name} • ${data.config_name}`;
    }
    return data?.git_commit_name ?? data?.config_name ?? buildId;
  }, [buildId, data]);

  const generalSections: ISection[] = useMemo(() => {
    if (!data) {
      return [];
    }
    return [
      {
        title: buildDetailsTitle,
        subtitle: <ButtonOpenLogSheet setSheetToLog={setSheetToLog} />,
        leftIcon: <StatusIcon status={data?.valid} />,
        eyebrow: formatMessage({ id: 'buildDetails.buildDetails' }),
        subsections: [
          {
            infos: [
              {
                title: 'global.tree',
                linkText: valueOrEmpty(data.tree_name),
              },
              {
                title: 'buildDetails.gitUrl',
                linkText: shouldTruncate(
                  valueOrEmpty(data.git_repository_url),
                ) ? (
                  <TruncatedValueTooltip
                    value={data.git_repository_url}
                    isUrl={true}
                  />
                ) : (
                  <span>{valueOrEmpty(data.git_repository_url)}</span>
                ),
                link: data.git_repository_url,
              },
              {
                title: 'buildDetails.gitBranch',
                linkText: valueOrEmpty(data.git_repository_branch),
              },
              {
                title: 'buildDetails.gitCommit',
                linkText: valueOrEmpty(data.git_commit_hash),
                copyValue: valueOrEmpty(data.git_commit_hash),
              },
              {
                title: 'buildDetails.gitDescribe',
                linkText: valueOrEmpty(data.git_commit_name),
              },
              {
                title: 'globalDetails.gitCommitTag',
                linkText: valueOrEmpty(data.git_commit_tags?.[0]),
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
                linkText: getBuildStatus(data.valid).toUpperCase(),
                icon: <StatusIcon status={data?.valid} className="text-xl" />,
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
              {
                title: 'buildDetails.buildId',
                linkText: buildId,
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
                link: data.log_url,
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
  }, [data, buildDetailsTitle, setSheetToLog, formatMessage, buildId]);

  const sectionsData: ISection[] = useMemo(() => {
    return [...generalSections, miscSection, filesSection].filter(
      section => section !== undefined,
    );
  }, [generalSections, miscSection, filesSection]);

  const buildDetailsTabTitle: string = useMemo(() => {
    const buildTitle = `${data?.tree_name} ${data?.git_commit_name}`;
    return formatMessage(
      { id: 'title.buildDetails' },
      { buildName: getTitle(buildTitle, isLoading) },
    );
  }, [data?.git_commit_name, data?.tree_name, formatMessage, isLoading]);

  return (
    <PageWithTitle title={buildDetailsTabTitle}>
      <MemoizedBuildDetailsOGTags
        tabTitle={buildDetailsTabTitle}
        descriptionTitle={buildDetailsTitle}
        data={data}
      />
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
          <Sheet open={logOpen} onOpenChange={logOpenChange}>
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
              error={issueError?.message}
            />
            <LogOrJsonSheetContent
              type={sheetType}
              jsonContent={jsonContent}
              hideIssueSection
              logUrl={data?.log_url}
              logExcerpt={data?.log_excerpt}
            />
          </Sheet>
        </ErrorBoundary>
      </QuerySwitcher>
    </PageWithTitle>
  );
};

export default BuildDetails;
