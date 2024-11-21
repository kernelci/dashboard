import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useParams, useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { Skeleton } from '@/components/Skeleton';

import { useTestsTab } from '@/api/treeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';

import MemoizedStatusChart from '@/components/Cards/StatusChart';
import MemoizedConfigList from '@/components/Cards/ConfigsList';
import MemoizedErrorsSummary from '@/components/Cards/ErrorsSummary';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';

import { TestsTable } from '@/components/TestsTable/TestsTable';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

interface TestsTabProps {
  reqFilter: Record<string, string[]>;
}

const TestsTab = ({ reqFilter }: TestsTabProps): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { isLoading, data, error } = useTestsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
  });

  const { tableFilter, diffFilter } = useSearch({
    from: '/tree/$treeId/',
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
        search: s => s,
      };
    },
    [treeId],
  );

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              bootsTable: previousParams.tableFilter.bootsTable,
              buildsTable: previousParams.tableFilter.buildsTable,
              testsTable: filter,
            },
          };
        },
      });
    },
    [navigate],
  );

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.success" />
      </div>
    );
  }

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  if (!data) return <div />;

  if (data.testHistory.length < 1) {
    return (
      <BaseCard
        title={<FormattedMessage id="global.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
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
          <MemoizedStatusChart
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={data.testStatusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="global.configs" />}
            configStatusCounts={data.testConfigs}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.testArchSummary}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={data.testIssues}
            failedWithUnknownIssues={data.failedTestsWithUnknownIssues}
          />
        </div>
        <div>
          <TreeCommitNavigationGraph />
          <MemoizedHardwareTested
            title={<FormattedMessage id="testsTab.hardwareTested" />}
            environmentCompatible={data.testEnvironmentCompatible}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={data.testStatusSummary}
        />
        <TreeCommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="global.configs" />}
              configStatusCounts={data.testConfigs}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.testArchSummary}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={data.testIssues}
              failedWithUnknownIssues={data.failedTestsWithUnknownIssues}
            />
          </div>
          <div>
            <MemoizedHardwareTested
              title={<FormattedMessage id="testsTab.hardwareTested" />}
              environmentCompatible={data.testEnvironmentCompatible}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>

      <TestsTable
        testHistory={data.testHistory}
        onClickFilter={onClickFilter}
        filter={tableFilter.testsTable}
        getRowLink={getRowLink}
        updatePathFilter={updatePathFilter}
        currentPathFilter={currentPathFilter}
      />
    </div>
  );
};

export default TestsTab;
