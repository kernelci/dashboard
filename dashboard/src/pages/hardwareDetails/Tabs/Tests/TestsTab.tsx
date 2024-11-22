import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import MemoizedStatusChart from '@/components/Cards/StatusChart';
import MemoizedIssuesList from '@/components/Cards/IssuesList';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';

import { MemoizedConfigList, MemoizedErrorsSummary } from '../Boots/BootsTab';

import HardwareDetailsTestTable from './HardwareDetailsTestsTable';

interface TTestsTab {
  tests: THardwareDetails['tests'];
  hardwareId: string;
}

const TestsTab = ({ tests, hardwareId }: TTestsTab): JSX.Element => {
  const { tableFilter, diffFilter } = useSearch({
    from: '/hardware/$hardwareId',
  });
  const currentPathFilter = diffFilter.testPath
    ? Object.keys(diffFilter.testPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

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
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={tests.archSummary}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={tests.issues}
            failedWithUnknownIssues={tests.failedWithUnknownIssues}
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
              failedWithUnknownIssues={tests.failedWithUnknownIssues}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <HardwareDetailsTestTable
        testHistory={tests.history}
        filter={tableFilter.testsTable}
        hardwareId={hardwareId}
        onClickFilter={onClickFilter}
        updatePathFilter={updatePathFilter}
        currentPathFilter={currentPathFilter}
      />
    </div>
  );
};
export default TestsTab;
