import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import { BootsTable } from '@/components/BootsTable/BootsTable';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import type {
  HardwareSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

import {
  zTableFilterInfoDefault,
  type TestsTableFilter,
} from '@/types/tree/TreeDetails';

import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedStatusCard from '@/components/Tabs/Tests/StatusCard';
import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';
import { MemoizedPlatformsCard } from '@/components/Cards/PlatformsCard';

import { sanitizePlatforms } from '@/utils/utils';

import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';
import { RedirectFrom } from '@/types/general';
import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';

interface IBootsTab {
  hardwareId: string;
  trees: HardwareSummary['trees'];
  bootsSummary: HardwareSummary['boots'];
  fullDataResult?: UseQueryResult<THardwareDetails>;
}

const BootsTab = ({
  hardwareId,
  trees,
  bootsSummary,
  fullDataResult,
}: IBootsTab): JSX.Element => {
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
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              bootsTable: newFilter,
            },
          };
        },
      });
    },
    [navigate],
  );

  const platformItems = useMemo(
    () => sanitizePlatforms(bootsSummary.platforms),
    [bootsSummary.platforms],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="bootsTab.bootStatus" />}
            statusCounts={bootsSummary.status}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={bootsSummary.architectures}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={bootsSummary.issues}
            failedWithUnknownIssues={bootsSummary.unknown_issues}
            diffFilter={diffFilter}
            issueFilterSection="bootIssue"
            detailsId={hardwareId}
            pageFrom={RedirectFrom.Hardware}
          />
        </div>
        <div>
          <HardwareCommitNavigationGraph
            trees={trees}
            hardwareId={hardwareId}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={bootsSummary.configs}
            diffFilter={diffFilter}
          />
          <MemoizedPlatformsCard
            platforms={platformItems}
            issueFilterSection="bootPlatform"
            diffFilter={diffFilter}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={bootsSummary.status}
        />
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={bootsSummary.configs}
              diffFilter={diffFilter}
            />
            <MemoizedPlatformsCard
              platforms={platformItems}
              issueFilterSection="bootPlatform"
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={bootsSummary.architectures}
              diffFilter={diffFilter}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={bootsSummary.issues}
              failedWithUnknownIssues={bootsSummary.unknown_issues}
              diffFilter={diffFilter}
              issueFilterSection="bootIssue"
              detailsId={hardwareId}
              pageFrom={RedirectFrom.Hardware}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <HardwareDetailsTabsQuerySwitcher
        fullDataResult={fullDataResult}
        tabData={fullDataResult?.data?.boots}
      >
        <BootsTable
          tableKey="hardwareDetailsBoots"
          getRowLink={getRowLink}
          filter={tableFilter.bootsTable}
          testHistory={fullDataResult?.data?.boots}
          onClickFilter={onClickFilter}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
        />
      </HardwareDetailsTabsQuerySwitcher>
    </div>
  );
};
export default BootsTab;
