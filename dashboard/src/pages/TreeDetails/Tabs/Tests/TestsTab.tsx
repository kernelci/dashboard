import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useParams, useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { Skeleton } from '@/components/Skeleton';

import { useTreeDetails } from '@/api/treeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

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
import type { TFilter } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

interface TestsTabProps {
  reqFilter: TFilter;
}

const TestsTab = ({ reqFilter }: TestsTabProps): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { isLoading, data, error } = useTreeDetails({
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
          <MemoizedStatusCard
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={data.testStatusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="global.configs" />}
            configStatusCounts={data.testConfigs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.testArchSummary}
            diffFilter={diffFilter}
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
            diffFilter={diffFilter}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={data.testStatusSummary}
        />
        <TreeCommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="global.configs" />}
              configStatusCounts={data.testConfigs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.testArchSummary}
              diffFilter={diffFilter}
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
              diffFilter={diffFilter}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>

      <TestsTable
        tableKey="treeDetailsTests"
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
