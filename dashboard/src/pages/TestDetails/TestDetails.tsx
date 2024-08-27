import { useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import { useMemo } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';

import { GiFlatPlatform } from 'react-icons/gi';

import { useTestDetails } from '@/api/TestDetails';

import type { TTestDetails } from '@/types/tree/TestDetails';

import BaseCard from '@/components/Cards/BaseCard';

import CodeBlock from '@/components/Filter/CodeBlock';

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
  test: TTestDetails;
};

const emptyValue = '-';
const valueOrEmpty = (value: string | undefined): string => value || emptyValue;

const maxTextLength = 50;

const truncateBigText = (text: string | undefined): string | undefined =>
  text && text.length > maxTextLength
    ? text.slice(0, maxTextLength) + '...'
    : valueOrEmpty(text);

const LogExcerpt = ({ test }: TTestDetailsDefaultProps): JSX.Element => {
  return (
    <BaseCard
      title={<FormattedMessage id="testDetails.logExcerpt" />}
      className="gap-0"
      content={<CodeBlock code={test.log_excerpt ?? ''} />}
    />
  );
};

const TestDetailsSection = ({ test }: { test: TTestDetails }): JSX.Element => {
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
        icon: <PiComputerTowerThin className="text-blue" />,
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
        icon: <GiFlatPlatform className="text-blue" />,
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
  const searchParams = useSearch({ from: '/tree/$treeId/test/$testId/' });
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

  if (!data) {
    return (
      <div>
        <FormattedMessage id="testDetails.notFound" />
      </div>
    );
  }

  return (
    <>
      <div className="w-100 px-5">
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
                <FormattedMessage id="tree.details" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <h1 className="mb-4 border-b border-gray-300 pb-3 text-2xl font-bold">
          {data.path}
        </h1>
        <LogExcerpt test={data} />
        <TestDetailsSection test={data} />
      </div>
    </>
  );
};

export default TestDetails;
