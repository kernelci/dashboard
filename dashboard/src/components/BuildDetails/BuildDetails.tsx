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

import { formatDate, getTitle } from '@/utils/utils';

import IssueSection from '@/components/Issue/IssueSection';

import { shouldTruncate, truncateBigText, valueOrEmpty } from '@/lib/string';

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

import MemoizedLinkItem from '@/components/DetailsLink';
import { LinkIcon } from '@/components/Icons/Link';
import { processLogData } from '@/hooks/useLogData';

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
  const logData = useMemo(() => {
    if (!data) {
      return undefined;
    }
    return processLogData(buildId, { type: 'build', ...data });
  }, [buildId, data]);

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

  const treeDetailsLink = useMemo(
    () => (
      <MemoizedLinkItem
        to="/tree/$treeId"
        params={{ treeId: data?.git_commit_hash }}
        state={s => s}
        search={s => ({
          origin: s.origin,
          treeInfo: {
            gitBranch: data?.git_repository_branch,
            gitUrl: data?.git_repository_url,
            treeName: data?.tree_name,
            commitName: data?.git_commit_name,
            headCommitHash: data?.git_commit_hash,
          },
        })}
      >
        {truncateBigText(data?.git_commit_hash)}
        <LinkIcon className="text-blue text-xl" />
      </MemoizedLinkItem>
    ),
    [data],
  );

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: data?.misc,
      title: formatMessage({ id: 'commonDetails.miscData' }),
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
      title: formatMessage({ id: 'commonDetails.artifacts' }),
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
        leftIcon: <StatusIcon status={data?.status} />,
        eyebrow: formatMessage({ id: 'buildDetails.buildDetails' }),
        subsections: [
          {
            infos: [
              {
                title: 'global.status',
                linkText: data.status.toUpperCase(),
                icon: <StatusIcon status={data.status} className="text-xl" />,
              },
              {
                title: 'buildDetails.gitDescribe',
                linkText: valueOrEmpty(data.git_commit_name),
              },
              {
                title: 'global.tree',
                linkText: valueOrEmpty(data.tree_name),
              },
              {
                title: 'commonDetails.gitRepositoryBranch',
                linkText: valueOrEmpty(data.git_repository_branch),
              },
              {
                title: 'commonDetails.gitCommitHash',
                linkText: valueOrEmpty(data.git_commit_hash),
                linkComponent: treeDetailsLink,
                copyValue: valueOrEmpty(data.git_commit_hash),
              },
              {
                title: 'commonDetails.gitRepositoryUrl',
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
                title: 'commonDetails.gitCommitTag',
                linkText: valueOrEmpty(data.git_commit_tags?.[0]),
              },
              {
                title: 'global.command',
                linkText: valueOrEmpty(data.command),
              },
              {
                title: 'global.architecture',
                linkText: valueOrEmpty(data.architecture),
              },
              {
                title: 'global.compiler',
                linkText: valueOrEmpty(data.compiler),
              },
              {
                title: 'global.config',
                linkText: valueOrEmpty(data.config_name),
              },
              {
                title: 'global.date',
                linkText: formatDate(valueOrEmpty(data.start_time)),
              },
              {
                title: 'global.buildTime',
                linkText: data.duration ? `${data.duration} sec` : '-',
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
  }, [
    data,
    buildDetailsTitle,
    setSheetToLog,
    formatMessage,
    buildId,
    treeDetailsLink,
  ]);

  const sectionsData: ISection[] = useMemo(() => {
    return [...generalSections, filesSection, miscSection].filter(
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
              logData={logData}
            />
          </Sheet>
        </ErrorBoundary>
      </QuerySwitcher>
    </PageWithTitle>
  );
};

export default BuildDetails;
