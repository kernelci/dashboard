import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

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

import HardwareDetailsTestTable from './HardwareDetailsTestsTable';

interface TTestsTab {
  tests: THardwareDetails['tests'];
  hardwareId: string;
}

const TestsTab = ({ tests, hardwareId }: TTestsTab): JSX.Element => {
  const { tableFilter } = useSearch({ from: '/hardware/$hardwareId' });
  const {
    diffFilter,
  }: { diffFilter: Record<string, Record<string, boolean>> } = useSearch({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const onClickFilter = useCallback(
    (newFilter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...previousParams.tableFilter,
              testsTable: newFilter,
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
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={tests.statusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={tests.configs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={tests.archSummary}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={tests.issues}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={tests.statusSummary}
        />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={tests.configs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={tests.archSummary}
              diffFilter={diffFilter}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={tests.issues}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <HardwareDetailsTestTable
        testHistory={tests.history}
        filter={tableFilter.testsTable}
        hardwareId={hardwareId}
        onClickFilter={onClickFilter}
      />
    </div>
  );
};
export default TestsTab;
