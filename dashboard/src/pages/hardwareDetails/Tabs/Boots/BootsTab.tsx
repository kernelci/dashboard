import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedStatusChart from '@/components/Cards/StatusChart';
import MemoizedConfigList from '@/components/Cards/ConfigsList';
import MemoizedErrorsSummary from '@/components/Cards/ErrorsSummary';
import MemoizedIssuesList from '@/components/Cards/IssuesList';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

interface TBootsTab {
  boots: THardwareDetails['boots'];
  hardwareId: string;
}

const BootsTab = ({ boots, hardwareId }: TBootsTab): JSX.Element => {
  const { tableFilter } = useSearch({ from: '/hardware/$hardwareId' });

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
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={boots.archSummary}
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
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={boots.archSummary}
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
