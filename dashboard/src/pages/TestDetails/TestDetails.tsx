import { useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import { useMemo } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';

import { GiFlatPlatform } from 'react-icons/gi';

import { MdFolderOpen } from 'react-icons/md';

import { useTestDetails, useTestIssues } from '@/api/TestDetails';

import type { TTestDetails } from '@/types/tree/TestDetails';

import { ISubsection, Subsection } from '@/components/Section/Section';

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

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { LogSheet } from '../TreeDetails/Tabs/LogSheet';

const emptyValue = '-';
const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const TestDetailsSection = ({ test }: { test: TTestDetails }): JSX.Element => {
  const intl = useIntl();
  const hardware: string =
    test.environment_compatible?.join(' | ') ??
    intl.formatMessage({ id: 'global.unknown' });

  const buildDetailsLink =
    `${window.location.origin}` +
    `/tree/${test.git_commit_hash}/build/${test.build_id}` +
    `${window.location.search}`;

  const hasUsefulLogInfo = test.log_url || test.log_excerpt;

  const infos: ISubsection['infos'] = useMemo(() => {
    const baseInfo: ISubsection['infos'] = [
      {
        title: 'testDetails.status',
        linkText: truncateBigText(test.status),
      },
      {
        title: 'testDetails.path',
        linkText: valueOrEmpty(test.path),
      },
      {
        title: 'testDetails.arch',
        linkText: valueOrEmpty(test.architecture),
        icon: <PiComputerTowerThin className="text-blue" />,
      },
      {
        title: 'testDetails.compiler',
        linkText: valueOrEmpty(test.compiler),
      },
      {
        title: 'global.logs',
        icon: hasUsefulLogInfo ? (
          <MdFolderOpen className="text-blue" />
        ) : undefined,
        linkText: truncateBigText(valueOrEmpty(test.log_url)),
        wrapperComponent: hasUsefulLogInfo ? SheetTrigger : undefined,
      },
      {
        title: 'testDetails.gitCommitHash',
        linkText: valueOrEmpty(test.git_commit_hash),
      },
      {
        title: 'testDetails.gitRepositoryUrl',
        linkText: truncateBigText(valueOrEmpty(test.git_repository_url)),
        link: test.git_repository_url,
      },
      {
        title: 'testDetails.gitRepositoryBranch',
        linkText: valueOrEmpty(test.git_repository_branch),
      },
      {
        title: 'testDetails.buildInfo',
        linkText: truncateBigText(test.build_id),
        link: buildDetailsLink,
      },
      {
        title: 'testDetails.hardware',
        linkText: hardware,
        icon: <GiFlatPlatform className="text-blue" />,
      },
      {
        title: 'global.startTime',
        linkText: (
          <TooltipDateTime
            dateTime={test.start_time}
            lineBreak={true}
            showLabelTime={true}
            showLabelTZ={true}
          />
        ),
      },
    ];

    return baseInfo;
  }, [
    test.status,
    test.path,
    test.architecture,
    test.compiler,
    test.log_url,
    test.git_commit_hash,
    test.git_repository_url,
    test.git_repository_branch,
    test.build_id,
    test.start_time,
    hasUsefulLogInfo,
    buildDetailsLink,
    hardware,
  ]);
  return <Subsection infos={infos} />;
};

const TestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/tree/$treeId/test/$testId/' });
  const { testId, treeId } = useParams({ from: '/tree/$treeId/test/$testId/' });
  const { data, error, isLoading } = useTestDetails(testId ?? '');
  const issuesQueryResult = useTestIssues(testId);

  if (error) {
    return (
      <div>
        <FormattedMessage id="testDetails.failedToFetch" />
      </div>
    );
  }

  if (isLoading) return <FormattedMessage id="global.loading" />;

  if (!data) {
    return (
      <div>
        <FormattedMessage id="testDetails.notFound" />
      </div>
    );
  }

  return (
    <Sheet>
      <div className="w-100 px-5 pb-8">
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
                <FormattedMessage id="test.details" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mb-4 text-2xl font-bold">{data.path}</h1>
        <TestDetailsSection test={data} />
        <IssueSection {...issuesQueryResult} />
      </div>
      <LogSheet logUrl={data.log_url} logExcerpt={data.log_excerpt} />
    </Sheet>
  );
};

export default TestDetails;
