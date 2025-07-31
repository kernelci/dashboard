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

import { processLogData } from '@/hooks/useLogData';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

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

    const archCompilerConfigText =
      valueOrEmpty(data.architecture) +
      ' / ' +
      valueOrEmpty(data.compiler) +
      ' / ' +
      valueOrEmpty(data.config_name);
    const gitUrl = valueOrEmpty(data.git_repository_url);
    const logUrl = valueOrEmpty(data.log_url);
    const configUrl = valueOrEmpty(data.config_url);

    return [
      {
        title: buildDetailsTitle,
        subtitle: (
          <div>
            <span className="text-[18px]">
              {formatDate(valueOrEmpty(data.start_time), false, true)}
            </span>
            <ButtonOpenLogSheet setSheetToLog={setSheetToLog} />
          </div>
        ),
        leftIcon: <StatusIcon status={data.status} />,
        subsections: [
          {
            infos: [
              {
                title: 'global.status',
                linkText: data.status.toUpperCase(),
                icon: <StatusIcon status={data.status} className="text-xl" />,
              },
              {
                title: 'global.treeBranchHash',
                linkComponent: (
                  <TreeDetailsLink
                    treeName={data.tree_name}
                    gitBranch={data.git_repository_branch}
                    commitHash={data.git_commit_hash}
                    gitUrl={data.git_repository_url}
                    commitName={data.git_commit_name}
                  />
                ),
                copyValue: valueOrEmpty(data.git_commit_hash),
              },
              {
                title: 'commonDetails.gitRepositoryUrl',
                linkText: shouldTruncate(gitUrl) ? (
                  <TruncatedValueTooltip value={gitUrl} isUrl={true} />
                ) : (
                  <span>{gitUrl}</span>
                ),
                link: data.git_repository_url,
              },
              {
                title: 'commonDetails.gitCommitTag',
                linkText: valueOrEmpty(data.git_commit_tags?.[0]),
              },
              {
                title: 'buildDetails.gitDescribe',
                linkText: valueOrEmpty(data.git_commit_name),
              },
              {
                title: 'global.archCompilerConfig',
                linkText: archCompilerConfigText,
              },
              {
                title: 'global.command',
                linkText: valueOrEmpty(data.command),
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
                linkText: shouldTruncate(logUrl) ? (
                  <TruncatedValueTooltip value={logUrl} isUrl={true} />
                ) : (
                  <span>{logUrl}</span>
                ),
                link: data.log_url,
              },
              {
                title: 'buildDetails.kernelConfig',
                linkText: shouldTruncate(configUrl) ? (
                  <TruncatedValueTooltip value={configUrl} isUrl={true} />
                ) : (
                  <span>{configUrl}</span>
                ),
                link: data.config_url,
              },
            ],
          },
        ],
      },
    ];
  }, [data, buildDetailsTitle, setSheetToLog, buildId]);

  const buildDetailsTabTitle: string = useMemo(() => {
    const buildTitle = `${data?.tree_name} ${data?.git_commit_name}`;
    return formatMessage(
      { id: 'title.buildDetails' },
      { buildName: getTitle(buildTitle, isLoading) },
    );
  }, [data?.git_commit_name, data?.tree_name, formatMessage, isLoading]);

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="details"
        args={{
          cmdName: 'build',
          id: buildId,
          'download-logs': true,
          json: true,
        }}
      />
    ),
    [buildId],
  );

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
            emptyLabel="buildDetails.notFound"
          />
        }
      >
        <ErrorBoundary FallbackComponent={UnexpectedError}>
          <Sheet open={logOpen} onOpenChange={logOpenChange}>
            <div className="flex flex-col gap-4 pb-10">
              {breadcrumb}
              <SectionGroup sections={generalSections} />
              <BuildDetailsTestSection
                buildId={buildId ?? ''}
                onClickFilter={onClickFilter}
                tableFilter={tableFilter}
                getRowLink={getTestTableRowLink}
              />
              {miscSection && <SectionGroup sections={[miscSection]} />}
              {issueData && (
                <IssueSection
                  data={issueData}
                  status={issueStatus}
                  error={issueError?.message}
                />
              )}
              {filesSection && <SectionGroup sections={[filesSection]} />}
              {kcidevComponent}
            </div>
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
