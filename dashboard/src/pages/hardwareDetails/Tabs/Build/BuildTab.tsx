import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import type {
  HardwareDetailsSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';
import { sanitizeArchs, sanitizeConfigs } from '@/utils/utils';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';

import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';
import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';
import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';

import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';

import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { HardwareDetailsBuildsTable } from './HardwareDetailsBuildsTable';

interface IBuildTab {
  trees: HardwareDetailsSummary['common']['trees'];
  hardwareId: string;
  buildsSummary: HardwareDetailsSummary['summary']['builds'];
  fullDataResult?: UseQueryResult<THardwareDetails>;
}

const BuildTab = ({
  hardwareId,
  trees,
  buildsSummary,
  fullDataResult,
}: IBuildTab): JSX.Element => {
  const navigate = useNavigate({
    from: '/hardware/$hardwareId',
  });

  const { diffFilter } = useSearch({
    from: '/_main/hardware/$hardwareId',
  });

  const toggleFilterBySection = useCallback(
    (filterSectionKey: string, filterSection: TFilterObjectsKeys): void => {
      navigate({
        search: previousParams => {
          const { diffFilter: currentDiffFilter } = previousParams;
          const newFilter = generateDiffFilter(
            filterSectionKey,
            filterSection,
            currentDiffFilter,
          );

          return {
            ...previousParams,
            diffFilter: newFilter,
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const archSummary = useMemo(
    () => sanitizeArchs(buildsSummary.architectures),
    [buildsSummary.architectures],
  );

  const configsItems = useMemo(
    () => sanitizeConfigs(buildsSummary.configs),
    [buildsSummary.configs],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="buildTab.buildStatus" />}
            toggleFilterBySection={toggleFilterBySection}
            statusCounts={buildsSummary.status}
            filterStatusKey="buildStatus"
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
        <div>
          <HardwareCommitNavigationGraph
            trees={trees}
            hardwareId={hardwareId}
          />
          <MemoizedConfigsCard
            configs={configsItems}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={buildsSummary.issues}
          failedWithUnknownIssues={buildsSummary.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="buildIssue"
          detailsId={hardwareId}
          pageFrom={RedirectFrom.Hardware}
        />
      </DesktopGrid>
      <MobileGrid>
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
        <MemoizedStatusCard
          title={<FormattedMessage id="buildTab.buildStatus" />}
          toggleFilterBySection={toggleFilterBySection}
          statusCounts={buildsSummary.status}
          filterStatusKey="buildStatus"
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedConfigsCard
            configs={configsItems}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={buildsSummary.issues}
            failedWithUnknownIssues={buildsSummary.unknown_issues}
            diffFilter={diffFilter}
            issueFilterSection="buildIssue"
            detailsId={hardwareId}
            pageFrom={RedirectFrom.Hardware}
          />
        </InnerMobileGrid>
      </MobileGrid>

      <div className="flex flex-col gap-4">
        <div className="text-lg">
          <FormattedMessage id="global.builds" />
        </div>
        <HardwareDetailsTabsQuerySwitcher
          fullDataResult={fullDataResult}
          tabData={fullDataResult?.data?.builds}
        >
          <HardwareDetailsBuildsTable
            buildsData={fullDataResult?.data?.builds}
            hardwareId={hardwareId}
          />
        </HardwareDetailsTabsQuerySwitcher>
      </div>
    </div>
  );
};

export default BuildTab;
