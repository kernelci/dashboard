import { useParams } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useMemo } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';

import { GiFlatPlatform } from 'react-icons/gi';

import { useTestDetails } from '@/api/TestDetails';

import type {
  StatusCount,
  TTestDetails,
  TTestFromTestDetails,
} from '@/types/tree/TestDetails';

import BaseCard, { IBaseCard } from '@/components/Cards/BaseCard';

import CodeBlock from '@/components/Filter/CodeBlock';

import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';
import { ISubsection, Subsection } from '@/components/Section/Section';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

type TTestDetailsDefaultProps = {
  test: TTestFromTestDetails;
};

interface IStatusChart extends Pick<TTestDetails, 'statusCount'> {
  title: IBaseCard['title'];
}

const emptyValue = '-';
const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const maxTextLength = 50;

const truncateBigText = (text: string | undefined): string | undefined =>
  text && text.length > maxTextLength
    ? text.slice(0, maxTextLength) + '...'
    : valueOrEmpty(text);

const StatusChart = ({ statusCount, title }: IStatusChart): JSX.Element => {
  const totalCount = Object.values(statusCount).reduce(
    (accumulator: number, count) => accumulator + (count ?? 0),
    0,
  );
  const chartElements = [
    {
      label: 'bootsTab.success',
      value: statusCount['PASS'] ?? 0,
      color: Colors.Green,
    },
    {
      label: 'global.failed',
      value: statusCount['FAIL'] ?? 0,
      color: Colors.Red,
    },
    {
      label: 'global.skiped',
      value: statusCount['SKIP'] ?? 0,
      color: Colors.Yellow,
    },
    {
      label: 'global.missed',
      value: statusCount['MISS'] ?? 0,
      color: Colors.Yellow,
    },
    {
      label: 'global.done',
      value: statusCount['DONE'] ?? 0,
      color: Colors.Yellow,
    },
    {
      label: 'global.error',
      value: statusCount['ERROR'] ?? 0,
      color: Colors.Red,
    },
  ] satisfies StatusChartValues[];

  const filteredChartElements = chartElements.filter(chartElement => {
    return chartElement.value > 0;
  });

  return (
    <BaseCard
      title={title}
      content={
        <StatusChartMemoized
          type="chart"
          elements={filteredChartElements}
          pieCentralLabel="Statuses"
          pieCentralDescription={<>{totalCount}</>}
        />
      }
    />
  );
};

export const MemoizedStatusChart = memo(StatusChart);

const LogExcerpt = ({ test }: TTestDetailsDefaultProps): JSX.Element => {
  return (
    <BaseCard
      title=<FormattedMessage id="testDetails.logExcerpt" />
      className="gap-0"
      content={<CodeBlock code={test.log_excerpt ?? ''} />}
    />
  );
};

const TestDetailsSection = ({
  test,
}: {
  test: TTestFromTestDetails;
}): JSX.Element => {
  const intl = useIntl();
  const infos: ISubsection['infos'] = useMemo(() => {
    const baseInfo = [
      {
        title: intl.formatMessage({ id: 'testDetails.status' }),
        linkText: truncateBigText(test.status),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.path' }),
        linkText: valueOrEmpty(test.path),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.arch' }),
        linkText: valueOrEmpty(test.architecture),
        icon: <PiComputerTowerThin className="text-lightBlue" />,
      },
      {
        title: intl.formatMessage({ id: 'testDetails.compiler' }),
        linkText: valueOrEmpty(test.compiler),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.logUrl' }),
        linkText: truncateBigText(valueOrEmpty(test.log_url)),
        link: valueOrEmpty(test.log_url),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.gitCommitHash' }),
        linkText: valueOrEmpty(test.git_commit_hash),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.gitRepositoryUrl' }),
        linkText: truncateBigText(valueOrEmpty(test.git_repository_url)),
        link: valueOrEmpty(test.git_repository_url),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.gitRepositoryBranch' }),
        linkText: valueOrEmpty(test.git_repository_branch),
      },
      {
        title: intl.formatMessage({ id: 'testDetails.platform' }),
        linkText:
          test.misc?.platform ??
          test.environment_misc?.platform ??
          intl.formatMessage({ id: 'global.unknown' }),
        icon: <GiFlatPlatform className="text-lightBlue" />,
      },
    ];
    return baseInfo;
  }, [
    intl,
    test.architecture,
    test.compiler,
    test.environment_misc?.platform,
    test.git_commit_hash,
    test.git_repository_branch,
    test.git_repository_url,
    test.log_url,
    test.misc?.platform,
    test.path,
    test.status,
  ]);
  return <Subsection infos={infos} />;
};

const TestDetails = (): JSX.Element => {
  const { testId, treeId } = useParams({ from: '/tree/$treeId/test/$testId/' });
  const { data, error, isLoading } = useTestDetails(testId ?? '');

  if (error) {
    return (
      <div>
        <FormattedMessage id="testDetails.failedToFetch" />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div>
        <FormattedMessage id="global.loading" />
      </div>
    );
  }

  // TODO Split the test already in the backend, both are unsafe
  const [currentTest, ..._unsafeDescendants] = data?.tests ?? [];

  if (!currentTest) {
    return (
      <div>
        <FormattedMessage id="testDetails.notFound" />
      </div>
    );
  }

  // const descendants = unsafeDescendants ?? [];

  return (
    <>
      {/*
      <pre className="overflow-x-auto">
        {JSON.stringify(currentTest, null, 2)}
      </pre>
      */}

      <div className="w-100 px-5">
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
              <BreadcrumbPage>
                <FormattedMessage id="tree.details" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mb-4 border-b border-gray-300 pb-3 text-2xl font-bold">
          {currentTest.path}
        </h1>
        <MemoizedStatusChart
          statusCount={data?.statusCount ?? ({} as StatusCount)}
          title="Test Status"
        />
        <LogExcerpt test={currentTest} />
        <TestDetailsSection test={currentTest} />
        {/*
      <TestDetailsTable tests={descendants} />;
      */}
      </div>
    </>
  );
};

export default TestDetails;
