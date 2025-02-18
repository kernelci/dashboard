import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import type {
  HardwareDetailsSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedStatusCard from '@/components/Tabs/Tests/StatusCard';
import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';
import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';
import { MemoizedPlatformsCard } from '@/components/Cards/PlatformsCard';

import { sanitizePlatforms } from '@/utils/utils';

import { RedirectFrom } from '@/types/general';

import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';

import HardwareDetailsTestTable from './HardwareDetailsTestsTable';

interface ITestsTab {
  hardwareId: string;
  trees: HardwareDetailsSummary['common']['trees'];
  testsSummary: HardwareDetailsSummary['summary']['tests'];
  fullDataResult?: UseQueryResult<THardwareDetails>;
}

const TestsTab = ({
  hardwareId,
  trees,
  testsSummary,
  fullDataResult,
}: ITestsTab): JSX.Element => {
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
        state: s => s,
      });
    },
    [navigate],
  );

  const onClickFilter = useCallback(
    (newFilter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: newFilter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const platformItems = useMemo(
    () => sanitizePlatforms(testsSummary.platforms),
    [testsSummary.platforms],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={testsSummary.status}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={testsSummary.architectures}
            diffFilter={diffFilter}
          />
        </div>
        <div>
          <HardwareCommitNavigationGraph
            trees={trees}
            hardwareId={hardwareId}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={testsSummary.configs}
            diffFilter={diffFilter}
          />
          <MemoizedPlatformsCard
            platforms={platformItems}
            issueFilterSection="testPlatform"
            diffFilter={diffFilter}
          />
        </div>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={testsSummary.issues}
          failedWithUnknownIssues={testsSummary.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="testIssue"
          detailsId={hardwareId}
          pageFrom={RedirectFrom.Hardware}
        />
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={testsSummary.status}
        />
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={testsSummary.configs}
              diffFilter={diffFilter}
            />
            <MemoizedPlatformsCard
              platforms={platformItems}
              issueFilterSection="testPlatform"
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={testsSummary.architectures}
              diffFilter={diffFilter}
            />
          </div>
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={testsSummary.issues}
            failedWithUnknownIssues={testsSummary.unknown_issues}
            diffFilter={diffFilter}
            issueFilterSection="testIssue"
            detailsId={hardwareId}
            pageFrom={RedirectFrom.Hardware}
          />
        </InnerMobileGrid>
      </MobileGrid>
      <HardwareDetailsTabsQuerySwitcher
        fullDataResult={fullDataResult}
        tabData={fullDataResult?.data?.tests}
      >
        <HardwareDetailsTestTable
          tableKey="hardwareDetailsTests"
          testHistory={fullDataResult?.data?.tests}
          filter={tableFilter.testsTable}
          hardwareId={hardwareId}
          onClickFilter={onClickFilter}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
        />
      </HardwareDetailsTabsQuerySwitcher>
    </div>
  );
};
export default TestsTab;
