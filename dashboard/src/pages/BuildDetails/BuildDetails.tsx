import { ImTree } from 'react-icons/im';

import { MdClose, MdCheck, MdFolderOpen } from 'react-icons/md';

import { BsFileEarmarkCode } from 'react-icons/bs';
import { FormattedMessage, useIntl } from 'react-intl';
import { ErrorBoundary } from 'react-error-boundary';
import { useMemo } from 'react';

import { useParams } from '@tanstack/react-router';

import SectionGroup from '@/components/Section/SectionGroup';
import { ISection } from '@/components/Section/Section';
import { useBuildDetails } from '@/api/BuildDetails';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import BuildDetailsTestSection from './BuildDetailsTestSection';

const emptyValue = '-';
const maxTextLength = 50;

const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const truncateBigText = (text: string | undefined): string | undefined =>
  text && text.length > maxTextLength
    ? text.slice(0, maxTextLength) + '...'
    : valueOrEmpty(text);

const BlueFolderIcon = (): JSX.Element => (
  <MdFolderOpen className="text-lightBlue" />
);

const BuildDetails = (): JSX.Element => {
  const { buildId, treeId } = useParams({
    from: '/tree/$treeId/build/$buildId/',
  });
  const { data, error } = useBuildDetails(buildId || '');
  const intl = useIntl();

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
                title: intl.formatMessage({ id: 'global.tree' }),
                linkText: valueOrEmpty(data.tree_name),
                icon: <ImTree className="text-lightBlue" />,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.gitUrl' }),
                linkText: truncateBigText(data.git_repository_url),
                link: data.git_repository_url,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.gitBranch' }),
                linkText: valueOrEmpty(data.git_repository_branch),
                icon: <ImTree className="text-lightBlue" />,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.gitCommit' }),
                linkText: valueOrEmpty(data.git_commit_hash),
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.gitDescribe' }),
                linkText: valueOrEmpty(data.git_commit_name),
              },
              {
                title: intl.formatMessage({ id: 'global.date' }),
                linkText: valueOrEmpty(data.timestamp),
              },
              {
                title: intl.formatMessage({ id: 'global.defconfig' }),
                linkText: valueOrEmpty(data.config_name),
              },
              {
                title: intl.formatMessage({ id: 'global.status' }),
                icon: data.valid ? (
                  <MdCheck className="text-green" />
                ) : (
                  <MdClose className="text-red" />
                ),
              },
              {
                title: intl.formatMessage({ id: 'global.architecture' }),
                linkText: valueOrEmpty(data.architecture),
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.buildTime' }),
                linkText: data.duration ? `${data.duration} sec` : emptyValue,
              },
            ],
          },
          {
            infos: [
              {
                title: intl.formatMessage({ id: 'buildDetails.compiler' }),
                linkText: valueOrEmpty(data.compiler),
              },
              {
                title: intl.formatMessage({ id: 'global.command' }),
                linkText: valueOrEmpty(valueOrEmpty(data.command)),
              },
            ],
          },
          {
            infos: [
              {
                title: intl.formatMessage({ id: 'buildDetails.buildLogs' }),
                linkText: truncateBigText(data.log_url),
                link: data.log_url,
                icon: data.log_url ? (
                  <BsFileEarmarkCode className="text-lightBlue" />
                ) : undefined,
              },
              {
                title: intl.formatMessage({ id: 'global.dtb' }),
                linkText: valueOrEmpty(data.misc?.dtb),
                icon: data.misc?.dtb ? <BlueFolderIcon /> : undefined,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.kernelConfig' }),
                linkText: truncateBigText(data.config_url),
                link: data.config_url,
                icon: data.config_url ? <BlueFolderIcon /> : undefined,
              },
              {
                title: intl.formatMessage({ id: 'global.modules' }),
                linkText: valueOrEmpty(data.misc?.modules),
                icon: data.misc?.modules ? <BlueFolderIcon /> : undefined,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.kernelImage' }),
                linkText: valueOrEmpty(data.misc?.kernel_type),
                icon: data.misc?.kernel_type ? <BlueFolderIcon /> : undefined,
              },
              {
                title: intl.formatMessage({ id: 'buildDetails.systemMap' }),
                linkText: valueOrEmpty(data.misc?.system_map),
                icon: data.misc?.system_map ? <BlueFolderIcon /> : undefined,
              },
            ],
          },
        ],
      },
    ];
  }, [data, intl]);

  //TODO: loading and 404
  if (!data) return <span></span>;
  if (error) return <UnexpectedError />;

  return (
    <ErrorBoundary FallbackComponent={UnexpectedError}>
      <Breadcrumb className="pb-6 pt-6">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink to="/tree">
              <FormattedMessage id="tree.path" />
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbLink to={`/tree/$treeId`} params={{ treeId: treeId }}>
            <FormattedMessage id="tree.details" />
          </BreadcrumbLink>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Build Details</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <SectionGroup sections={sectionsData} />
      {buildId && <BuildDetailsTestSection buildId={buildId} />}
    </ErrorBoundary>
  );
};

export default BuildDetails;
