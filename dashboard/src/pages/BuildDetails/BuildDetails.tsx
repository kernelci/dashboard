import { ImTree } from 'react-icons/im';

import { MdClose, MdCheck, MdFolderOpen } from 'react-icons/md';

import { FormattedMessage, useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo } from 'react';

import { useParams, useSearch } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import { ISection } from '@/components/Section/Section';
import { useBuildDetails, useBuildIssues } from '@/api/BuildDetails';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import { formatDate } from '@/utils/utils';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import IssueSection from '@/components/Issue/IssueSection';

import { truncateBigText } from '@/lib/string';

import { Sheet, SheetTrigger } from '@/components/Sheet';

import { LogSheet } from '@/pages/TreeDetails/Tabs/LogSheet';

import BuildDetailsTestSection from './BuildDetailsTestSection';

const emptyValue = '-';

const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const BlueFolderIcon = (): JSX.Element => (
  <MdFolderOpen className="text-blue" />
);

const BuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/tree/$treeId/build/$buildId/' });
  const { buildId, treeId } = useParams({
    from: '/tree/$treeId/build/$buildId/',
  });
  const { data, error } = useBuildDetails(buildId || '');
  const issuesQueryResult = useBuildIssues(buildId);

  const intl = useIntl();

  const hasUsefulLogInfo = data?.log_url || data?.log_excerpt;

  const sectionsData: ISection[] = useMemo(() => {
    if (!data) return [];
    return [
      {
        title: valueOrEmpty(
          data.git_commit_name
            ? `${data.git_commit_name} • ${data.config_name}`
            : data.config_name,
        ),
        eyebrow: intl.formatMessage({ id: 'buildDetails.buildDetails' }),
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
                linkText: truncateBigText(data.git_repository_url),
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
                title: 'global.defconfig',
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
                linkText: data.duration ? `${data.duration} sec` : emptyValue,
              },
            ],
          },
          {
            infos: [
              {
                title: 'buildDetails.compiler',
                linkText: valueOrEmpty(data.compiler),
              },
              {
                title: 'global.command',
                linkText: valueOrEmpty(valueOrEmpty(data.command)),
              },
            ],
          },
          {
            infos: [
              {
                title: 'buildDetails.buildLogs',
                linkText: truncateBigText(data.log_url),
                icon: hasUsefulLogInfo ? <BlueFolderIcon /> : undefined,
                wrapperComponent: hasUsefulLogInfo ? SheetTrigger : undefined,
              },
              {
                title: 'global.dtb',
                linkText: valueOrEmpty(data.misc?.dtb),
                icon: data.misc?.dtb ? <BlueFolderIcon /> : undefined,
              },
              {
                title: 'buildDetails.kernelConfig',
                linkText: truncateBigText(data.config_url),
                link: data.config_url,
                icon: data.config_url ? <BlueFolderIcon /> : undefined,
              },
              {
                title: 'global.modules',
                linkText: valueOrEmpty(data.misc?.modules),
                icon: data.misc?.modules ? <BlueFolderIcon /> : undefined,
              },
              {
                title: 'buildDetails.kernelImage',
                linkText: valueOrEmpty(data.misc?.kernel_type),
                icon: data.misc?.kernel_type ? <BlueFolderIcon /> : undefined,
              },
              {
                title: 'buildDetails.systemMap',
                linkText: valueOrEmpty(data.misc?.system_map),
                icon: data.misc?.system_map ? <BlueFolderIcon /> : undefined,
              },
            ],
          },
        ],
      },
    ];
  }, [data, hasUsefulLogInfo, intl]);

  //TODO: loading and 404
  if (!data) return <span></span>;
  if (error) return <UnexpectedError />;

  return (
    <ErrorBoundary FallbackComponent={UnexpectedError}>
      <Sheet>
        <Breadcrumb className="pb-6 pt-6">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink to="/tree" search={searchParams}>
                <FormattedMessage id="tree.path" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbLink
              to={`/tree/$treeId`}
              params={{ treeId: treeId }}
              search={searchParams}
            >
              <FormattedMessage id="tree.details" />
            </BreadcrumbLink>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>
                <FormattedMessage id="buildDetails.buildDetails" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <SectionGroup sections={sectionsData} />
        {buildId && <BuildDetailsTestSection buildId={buildId} />}
        <IssueSection {...issuesQueryResult} />
        <LogSheet logUrl={data.log_url} logExcerpt={data.log_excerpt} />
      </Sheet>
    </ErrorBoundary>
  );
};

export default BuildDetails;
