import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import { Skeleton } from '@/components/Skeleton';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';
import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';
import type { TestsTableFilter } from '@/types/tree/TreeDetails';
import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedStatusChart from '@/components/Tabs/Tests/StatusChart';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

interface BootsTabProps {
  reqFilter: Record<string, string[]>;
}

const BootsTab = ({ reqFilter }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const {
    diffFilter,
  }: { diffFilter: Record<string, Record<string, boolean>> } = useSearch({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({ from: '/tree/$treeId/' });

  const onClickFilter = useCallback(
    (newFilter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...previousParams.tableFilter,
              bootsTable: newFilter,
            },
          };
        },
      });
    },
    [navigate],
  );

  const { isLoading, data, error } = useTestsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
  });

  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: bootId,
        treeId: treeId,
      },
      search: s => s,
    }),
    [treeId],
  );

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.error" />
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

  if (data.bootHistory.length < 1) {
    return (
      <BaseCard
        title={<FormattedMessage id="bootsTab.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            <FormattedMessage id="bootsTab.info.description" />
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
            title={<FormattedMessage id="bootsTab.bootStatus" />}
            statusCounts={data.bootStatusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={data.bootConfigs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.bootArchSummary}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={data.bootIssues}
          />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedHardwareTested
            title={<FormattedMessage id="bootsTab.hardwareTested" />}
            environmentCompatible={data.bootEnvironmentCompatible}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={data.bootStatusSummary}
        />
        <CommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={data.bootConfigs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.bootArchSummary}
              diffFilter={diffFilter}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={data.bootIssues}
            />
          </div>
          <div>
            <MemoizedHardwareTested
              title={<FormattedMessage id="bootsTab.hardwareTested" />}
              environmentCompatible={data.bootEnvironmentCompatible}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <BootsTable
        filter={tableFilter.bootsTable}
        onClickFilter={onClickFilter}
        testHistory={data.bootHistory}
        getRowLink={getRowLink}
      />
    </div>
  );
};

export default BootsTab;
