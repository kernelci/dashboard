import { FormattedMessage } from 'react-intl';

import { useParams, useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { Skeleton } from '@/components/Skeleton';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';
import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';

import MemoizedStatusChart from '@/components/Cards/StatusChart';
import MemoizedConfigList from '@/components/Cards/ConfigsList';
import MemoizedErrorsSummary from '@/components/Cards/ErrorsSummary';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';

import { TestsTable } from './TestsTable';

interface TestsTabProps {
  reqFilter: Record<string, string[]>;
}

const TestsTab = ({ reqFilter }: TestsTabProps): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { isLoading, data, error } = useTestsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
  });

  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({ from: '/tree/$treeId' });

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
          />
        </div>
        <div>
          <CommitNavigationGraph />
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
        <CommitNavigationGraph />
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
        tableFilter={tableFilter}
      />
    </div>
  );
};

export default TestsTab;
