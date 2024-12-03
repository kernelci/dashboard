import { FormattedMessage, useIntl } from 'react-intl';

import { GiFlatPlatform } from 'react-icons/gi';

import { useMemo } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';
import { MdFolderOpen } from 'react-icons/md';

import { Link, useRouterState, useSearch } from '@tanstack/react-router';

import { FiLink } from 'react-icons/fi';

import { truncateBigText } from '@/lib/string';
import type { TTestDetails } from '@/types/tree/TestDetails';
import { Sheet, SheetTrigger } from '@/components/Sheet';
import { useTestDetails, useTestIssues } from '@/api/testDetails';

import { LogSheet } from '@/pages/TreeDetails/Tabs/LogSheet';

import { RedirectFrom } from '@/types/general';

import { Subsection } from '../Section/Section';
import type { ISubsection } from '../Section/Section';
import { TooltipDateTime } from '../TooltipDateTime';
import IssueSection from '../Issue/IssueSection';

const emptyValue = '-';
const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const TestDetailsSection = ({ test }: { test: TTestDetails }): JSX.Element => {
  const intl = useIntl();
  const historyState = useRouterState({ select: s => s.location.state });
  const searchParams = useSearch({ from: '/test/$testId' });
  const hardware: string =
    test.environment_compatible?.join(' | ') ??
    intl.formatMessage({ id: 'global.unknown' });

  const buildDetailsLink = useMemo(() => {
    let linkTo = '';
    let linkParams = {};
    if (historyState.from === RedirectFrom.Hardware && historyState.id) {
      linkTo = '/hardware/$hardwareId/build/$buildId';
      linkParams = { hardwareId: historyState.id, buildId: test.build_id };
    } else if (historyState.from === RedirectFrom.Tree && historyState.id) {
      linkTo = '/tree/$treeId/build/$buildId';
      linkParams = { treeId: historyState.id, buildId: test.build_id };
    } else {
      linkTo = '/build/$buildId';
      linkParams = { buildId: test.build_id };
    }

    return (
      <Link
        to={linkTo}
        params={linkParams}
        search={searchParams}
        className="flex flex-row items-center gap-1"
        target="_blank"
        rel="noreferrer"
      >
        {truncateBigText(test.build_id)}
        <FiLink className="text-blue" />
      </Link>
    );
  }, [historyState, test.build_id, searchParams]);

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
        linkComponent: buildDetailsLink,
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
  breadcrumb?: JSX.Element;
  testId?: string;
}

const TestDetails = ({
  breadcrumb,
  testId,
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
        <TestDetailsSection test={data} />
        <IssueSection {...issuesQueryResult} />
      </div>
      <LogSheet logUrl={data.log_url} logExcerpt={data.log_excerpt} />
    </Sheet>
  );
};

export default TestDetails;
