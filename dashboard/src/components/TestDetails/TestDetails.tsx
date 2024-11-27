import { FormattedMessage, useIntl } from 'react-intl';

import { GiFlatPlatform } from 'react-icons/gi';

import { useMemo } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';
import { MdFolderOpen } from 'react-icons/md';

import { truncateBigText } from '@/lib/string';
import type { TTestDetails } from '@/types/tree/TestDetails';
import { Sheet, SheetTrigger } from '@/components/Sheet';
import { useTestDetails, useTestIssues } from '@/api/TestDetails';

import { LogSheet } from '@/pages/TreeDetails/Tabs/LogSheet';

import { Subsection } from '../Section/Section';
import type { ISubsection } from '../Section/Section';
import { TooltipDateTime } from '../TooltipDateTime';
import IssueSection from '../Issue/IssueSection';

const emptyValue = '-';
const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const TestDetailsSection = ({
  test,
  context,
}: {
  test: TTestDetails;
  context: string;
}): JSX.Element => {
  const intl = useIntl();
  const hardware: string =
    test.environment_compatible?.join(' | ') ??
    intl.formatMessage({ id: 'global.unknown' });

  const buildDetailsLink =
    `${window.location.origin}` +
    `/${context}/${test.git_commit_hash}/build/${test.build_id}` +
    `${window.location.search}`;

  const hasUsefulLogInfo = test.log_url || test.log_excerpt;

  const infos: ISubsection['infos'] = useMemo(() => {
    const baseInfo: ISubsection['infos'] = [
      {
        title: 'global.status',
        linkText: truncateBigText(test.status),
      },
      {
        title: 'global.path',
        linkText: valueOrEmpty(test.path),
      },
      {
        title: 'global.arch',
        linkText: valueOrEmpty(test.architecture),
        icon: <PiComputerTowerThin className="text-blue" />,
      },
      {
        title: 'global.compiler',
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
        title: 'global.hardware',
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

interface TestsDetailsProps {
  breadcrumb: JSX.Element;
  testId?: string;
  context: string;
}

const TestDetails = ({
  breadcrumb,
  testId,
  context,
}: TestsDetailsProps): JSX.Element => {
  const { data, error, isLoading } = useTestDetails(testId ?? '');
  const issuesQueryResult = useTestIssues(testId ?? '');

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
        {breadcrumb}

        <h1 className="mb-4 text-2xl font-bold">{data.path}</h1>
        <TestDetailsSection test={data} context={context} />
        <IssueSection {...issuesQueryResult} />
      </div>
      <LogSheet logUrl={data.log_url} logExcerpt={data.log_excerpt} />
    </Sheet>
  );
};

export default TestDetails;
