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

import MemoizedStatusChart from '@/components/Tabs/Tests/StatusChart';
import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

interface TBootsTab {
  boots: THardwareDetails['boots'];
  hardwareId: string;
}

const BootsTab = ({ boots, hardwareId }: TBootsTab): JSX.Element => {
  const { tableFilter } = useSearch({ from: '/hardware/$hardwareId' });

  const {
    diffFilter,
  }: { diffFilter: Record<string, Record<string, boolean>> } = useSearch({
    from: '/tree/$treeId/',
  });

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
          <MemoizedStatusChart
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
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={boots.statusSummary}
        />
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
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <BootsTable
        getRowLink={getRowLink}
        filter={tableFilter.bootsTable}
        testHistory={boots.history}
        onClickFilter={onClickFilter}
      />
    </div>
  );
};
export default BootsTab;
