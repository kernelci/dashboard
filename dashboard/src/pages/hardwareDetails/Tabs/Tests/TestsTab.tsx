import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

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

import HardwareDetailsTestTable from './HardwareDetailsTestsTable';

interface TTestsTab {
  tests: THardwareDetails['tests'];
}

const TestsTab = ({ tests }: TTestsTab): JSX.Element => {
  const onClickFilter = useCallback(
    (filter: TestsTableFilter) => console.error('filter:', filter),
    [],
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
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={tests.archSummary}
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
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={tests.archSummary}
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
        filter={'all'}
        onClickFilter={onClickFilter}
      />
    </div>
  );
};
export default TestsTab;