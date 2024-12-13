import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { BootsTable } from '@/components/BootsTable/BootsTable';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedStatusCard from '@/components/Tabs/Tests/StatusCard';
import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';

interface TBootsTab {
  boots: THardwareDetails['boots'];
  trees: THardwareDetails['trees'];
  hardwareId: string;
}

const BootsTab = ({ boots, hardwareId, trees }: TBootsTab): JSX.Element => {
  const { tableFilter, diffFilter } = useSearch({
    from: '/hardware/$hardwareId',
  });
  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/hardware/$hardwareId/test/$testId',
      params: {
        testId: bootId,
        hardwareId: hardwareId,
      },
      search: s => s,
    }),
    [hardwareId],
  );

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

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

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="bootsTab.bootStatus" />}
            statusCounts={boots.statusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={boots.configs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={boots.archSummary}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={boots.issues}
            failedWithUnknownIssues={boots.failedWithUnknownIssues}
            diffFilter={diffFilter}
            issueFilterSection="bootIssue"
          />
        </div>
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={boots.statusSummary}
        />
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={boots.configs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={boots.archSummary}
              diffFilter={diffFilter}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={boots.issues}
              failedWithUnknownIssues={boots.failedWithUnknownIssues}
              diffFilter={diffFilter}
              issueFilterSection="bootIssue"
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <BootsTable
        tableKey="hardwareDetailsBoots"
        getRowLink={getRowLink}
        filter={tableFilter.bootsTable}
        testHistory={boots.history}
        onClickFilter={onClickFilter}
        updatePathFilter={updatePathFilter}
        currentPathFilter={currentPathFilter}
      />
    </div>
  );
};
export default BootsTab;
