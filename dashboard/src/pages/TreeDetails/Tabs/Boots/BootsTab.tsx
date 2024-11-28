import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import { Skeleton } from '@/components/Skeleton';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedStatusChart from '@/components/Cards/StatusChart';
import MemoizedConfigList from '@/components/Cards/ConfigsList';
import MemoizedErrorsSummary from '@/components/Cards/ErrorsSummary';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';
import type { TestsTableFilter } from '@/types/tree/TreeDetails';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

interface BootsTabProps {
  reqFilter: Record<string, string[]>;
}

const BootsTab = ({ reqFilter }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });
  const { tableFilter, diffFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/tree/$treeId/' });

  const updatePathFilter = useCallback(
    (pathFilter: string) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          diffFilter: {
            ...previousSearch.diffFilter,
            bootPath: pathFilter === '' ? undefined : { [pathFilter]: true },
          },
        }),
      });
    },
    [navigate],
  );

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
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.bootArchSummary}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={data.bootIssues}
            failedWithUnknownIssues={data.failedBootsWithUnknownIssues}
          />
        </div>
        <div>
          <TreeCommitNavigationGraph />
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
        <TreeCommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={data.bootConfigs}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.bootArchSummary}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={data.bootIssues}
              failedWithUnknownIssues={data.failedBootsWithUnknownIssues}
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
        updatePathFilter={updatePathFilter}
        currentPathFilter={currentPathFilter}
      />
    </div>
  );
};

export default BootsTab;
