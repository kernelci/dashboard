import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useParams, useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import { Skeleton } from '@/components/Skeleton';

import BaseCard from '@/components/Cards/BaseCard';

import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import MemoizedStatusCard from '@/components/Tabs/Tests/StatusCard';
import { RedirectFrom } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';
import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

interface TestsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
}

const TestsTab = ({ treeDetailsLazyLoaded }: TestsTabProps): JSX.Element => {
  const { treeId } = useParams({ from: '/_main/tree/$treeId' });

  const { full: fullQuery, summary: summaryQuery } = treeDetailsLazyLoaded;
  const { data, status, isLoading: fullIsLoading } = fullQuery;
  const { isLoading: isSummaryLoading, error: summaryError } = summaryQuery;
  const summaryData = treeDetailsLazyLoaded.summary.data?.summary.tests;

  const { tableFilter, diffFilter } = useSearch({
    from: '/_main/tree/$treeId',
  });

  const currentPathFilter = diffFilter.testPath
    ? Object.keys(diffFilter.testPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/tree/$treeId' });

  const updatePathFilter = useCallback(
    (pathFilter: string) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          diffFilter: {
            ...previousSearch.diffFilter,
            testPath: pathFilter === '' ? undefined : { [pathFilter]: true },
          },
        }),
      });
    },
    [navigate],
  );

  const getRowLink = useCallback(
    (bootId: string): LinkProps => {
      return {
        to: '/tree/$treeId/test/$testId',
        params: {
          testId: bootId,
          treeId: treeId,
        },
      };
    },
    [treeId],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const hardwareData = useMemo(() => {
    return {
      ...summaryData?.environment_compatible,
      ...summaryData?.environment_misc,
    };
  }, [summaryData?.environment_compatible, summaryData?.environment_misc]);

  if (summaryError || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.success" />
      </div>
    );
  }

  if (isSummaryLoading) {
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );
  }

  if (!summaryData) {
    return <div />;
  }

  if (!fullIsLoading && data?.tests.length === 0) {
    return (
      <BaseCard
        title={<FormattedMessage id="global.info" />}
        content={
          <p className="text-dark-gray p-4 text-[1.3rem]">
            <FormattedMessage id="testsTab.noTest" />
          </p>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={summaryData.status}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="global.configs" />}
            configStatusCounts={summaryData.configs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={summaryData.architectures}
            diffFilter={diffFilter}
          />
        </div>
        <div>
          <TreeCommitNavigationGraph />
          <MemoizedHardwareTested
            title={<FormattedMessage id="testsTab.hardwareTested" />}
            environmentCompatible={hardwareData}
            diffFilter={diffFilter}
          />
        </div>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={summaryData.issues}
          failedWithUnknownIssues={summaryData.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="testIssue"
          detailsId={treeId}
          pageFrom={RedirectFrom.Tree}
          issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
          extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
        />
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={summaryData.status}
        />
        <TreeCommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="global.configs" />}
              configStatusCounts={summaryData.configs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={summaryData.architectures}
              diffFilter={diffFilter}
            />
          </div>
          <div>
            <MemoizedHardwareTested
              title={<FormattedMessage id="testsTab.hardwareTested" />}
              environmentCompatible={hardwareData}
              diffFilter={diffFilter}
            />
          </div>
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={summaryData.issues}
            failedWithUnknownIssues={summaryData.unknown_issues}
            diffFilter={diffFilter}
            issueFilterSection="testIssue"
            detailsId={treeId}
            pageFrom={RedirectFrom.Tree}
            issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
            extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
          />
        </InnerMobileGrid>
      </MobileGrid>

      <QuerySwitcher status={status} data={data}>
        <TestsTable
          tableKey="treeDetailsTests"
          testHistory={data?.tests ?? []}
          onClickFilter={onClickFilter}
          filter={tableFilter.testsTable}
          getRowLink={getRowLink}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
        />
      </QuerySwitcher>
    </div>
  );
};

export default TestsTab;
