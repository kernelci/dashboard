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
import Section, { type ISection } from '@/components/Section/Section';
import { useBuildDetails, useBuildIssues } from '@/api/buildDetails';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { formatDate, getTitle } from '@/utils/utils';

import IssueSection from '@/components/Issue/IssueSection';

import { valueOrEmpty } from '@/lib/string';

import { Sheet } from '@/components/Sheet';

import type { TableFilter, TableStatusOption } from '@/types/tree/TreeDetails';

import type { SheetType } from '@/components/Sheet/LogOrJsonSheetContent';
import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import { getMiscSection } from '@/components/Section/MiscSection';

import { getFilesSection } from '@/components/Section/FilesSection';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { StatusIcon } from '@/components/Icons/StatusIcons';

import PageWithTitle from '@/components/PageWithTitle';

import { MemoizedBuildDetailsOGTags } from '@/components/OpenGraphTags/BuildDetailsOGTags';
import ButtonOpenLogSheet from '@/components/Button/ButtonOpenLogSheet';

import { processLogData } from '@/hooks/useLogData';

import { MemoizedKcidevCommandButton } from '@/components/Footer/KcidevCommandButton';
import { createResultDetailsCommand } from '@/components/Footer/kcidevCommand';

import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import { DetailsInfoCard } from '@/components/Cards/DetailsInfoCard';

import CopyButton from '@/components/Button/CopyButton';

import BuildDetailsTestSection from './BuildDetailsTestSection';

interface BuildDetailsProps {
  breadcrumb?: JSX.Element;
  onToggleFilter: (option: TableStatusOption) => void;
  tableFilter: TableFilter;
  getTestTableRowLink: (testId: string) => LinkProps;
}

const BuildDetails = ({
  breadcrumb,
  onToggleFilter,
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

    const gitUrl = valueOrEmpty(data.git_repository_url);
    const logUrl = valueOrEmpty(data.log_url);
    const configUrl = valueOrEmpty(data.config_url);

    return [
      {
        title: buildDetailsTitle,
        subtitle: <ButtonOpenLogSheet setSheetToLog={setSheetToLog} />,
        actions: (
          <MemoizedKcidevCommandButton
            command={createResultDetailsCommand('build', buildId)}
          />
        ),
        leftIcon: <StatusIcon status={data.status} showTooltip />,
        rightIcon: (
          <span className="text-dark-gray2 text-sm font-normal">
            {formatDate(valueOrEmpty(data.start_time), false, true)}
          </span>
        ),
        subsections: [
          {
            infos: [
              {
                children: (
                  <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                    <DetailsInfoCard
                      cardTitle="buildDetails.buildInfo"
                      data={[
                        {
                          title: 'global.status',
                          linkText: data.status,
                          icon: <StatusIcon status={data.status} />,
                        },
                        {
                          title: 'buildDetails.buildOrigin',
                          linkText: valueOrEmpty(data.build_origin),
                        },
                        {
                          title: 'buildDetails.buildId',
                          linkText: buildId,
                          span: 2,
                        },
                        {
                          title: 'global.buildTime',
                          linkText: data.duration
                            ? `${data.duration} sec`
                            : '-',
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
                          span: 2,
                        },
                        {
                          title: 'buildDetails.kernelConfig',
                          linkText: configUrl,
                          link: data.config_url,
                          span: 4,
                        },
                        {
                          title: 'global.command',
                          linkText: data.command ? undefined : '-',
                          linkComponent: data.command ? (
                            <div className="flex w-full min-w-0 items-center">
                              <pre className="min-w-0 flex-1 overflow-x-auto rounded-md bg-slate-100 p-2 font-mono text-sm [scrollbar-color:rgb(148_163_184)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-0.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-slate-400 [&::-webkit-scrollbar-track]:bg-transparent">
                                <code className="whitespace-nowrap">
                                  {data.command}
                                </code>
                              </pre>
                              <CopyButton value={data.command} />
                            </div>
                          ) : undefined,
                          span: 4,
                        },
                        {
                          title: 'global.logs',
                          linkText: logUrl,
                          link: data.log_url,
                          span: 4,
                        },
                      ]}
                    />
                    <DetailsInfoCard
                      cardTitle="commonDetails.gitInfo"
                      data={[
                        {
                          title: 'global.tree',
                          linkText: valueOrEmpty(data.tree_name),
                        },
                        {
                          title: 'globalTable.branch',
                          linkText: valueOrEmpty(data.git_repository_branch),
                        },
                        {
                          title: 'global.commitHash',
                          span: 2,
                          linkComponent: (
                            <span className="flex w-full min-w-0 items-center">
                              <TreeDetailsLink
                                className="min-w-0 flex-1"
                                treeName={data.tree_name}
                                gitBranch={data.git_repository_branch}
                                commitHash={data.git_commit_hash}
                                gitUrl={data.git_repository_url}
                                commitName={data.git_commit_name}
                              />
                              {data.git_commit_hash && (
                                <CopyButton value={data.git_commit_hash} />
                              )}
                            </span>
                          ),
                        },
                        {
                          title: 'global.commitTags',
                          linkText: valueOrEmpty(data.git_commit_tags?.[0]),
                          span: 2,
                        },
                        {
                          title: 'buildDetails.gitDescribe',
                          linkText: valueOrEmpty(data.git_commit_name),
                          span: 2,
                        },
                        {
                          title: 'global.repository',
                          linkText: gitUrl,
                          link: data.git_repository_url,
                          span: 4,
                        },
                      ]}
                    />
                  </div>
                ),
              },
            ],
          },
        ],
      },
    ];
  }, [data, buildDetailsTitle, setSheetToLog, buildId]);

  const buildDetailsTabTitle: string = useMemo(() => {
    const buildTitle =
      data?.tree_name || data?.git_commit_name
        ? `${data?.tree_name} ${data?.git_commit_name}`
        : buildId;
    return formatMessage(
      { id: 'title.buildDetails' },
      { buildName: getTitle(buildTitle, isLoading) },
    );
  }, [
    buildId,
    data?.git_commit_name,
    data?.tree_name,
    formatMessage,
    isLoading,
  ]);

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
                onToggleFilter={onToggleFilter}
                tableFilter={tableFilter}
                getRowLink={getTestTableRowLink}
              />
              {(miscSection || filesSection) && (
                <div
                  className={
                    miscSection && filesSection
                      ? 'grid grid-cols-1 items-start gap-4 lg:grid-cols-2'
                      : undefined
                  }
                >
                  {miscSection && <Section {...miscSection} card />}
                  {filesSection && <Section {...filesSection} card />}
                </div>
              )}
              {issueData && (
                <IssueSection
                  data={issueData}
                  status={issueStatus}
                  error={issueError?.message}
                />
              )}
            </div>
            <LogOrJsonSheetContent
              type={sheetType}
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
