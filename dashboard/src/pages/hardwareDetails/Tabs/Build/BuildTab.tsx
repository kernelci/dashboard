import { FormattedMessage } from 'react-intl';

import { useMemo } from 'react';

import { useSearch } from '@tanstack/react-router';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import { sanitizeArchs, sanitizeBuilds, sanitizeConfigs } from '@/utils/utils';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/Builds/StatusCard';

import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';
import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';
import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';

import { HardwareDetailsBuildsTable } from './HardwareDetailsBuildsTable';

interface TBuildTab {
  builds: THardwareDetails['builds'];
  trees: THardwareDetails['trees'];
  hardwareId: string;
}

const BuildTab = ({ builds, hardwareId, trees }: TBuildTab): JSX.Element => {
  const { diffFilter } = useSearch({
    from: '/hardware/$hardwareId/',
  });

  //TODO: implement this function to filter details by data list

  const toggleFilterBySection = console.error;
  /* useCallback(
    (filterSectionKey: string, filterSection: TFilterObjectsKeys): void => {
      navigate({
        search: previousParams => {
          const { diffFilter: currentDiffFilter } = previousParams;
          const newFilter = structuredClone(currentDiffFilter);
          // This seems redundant but we do this to keep the pointer to newFilter[filterSection]
          newFilter[filterSection] = newFilter[filterSection] ?? {};
          const configs = newFilter[filterSection];
          if (configs[filterSectionKey]) {
            delete configs[filterSectionKey];
          } else {
            configs[filterSectionKey] = true;
          }

          return {
            ...previousParams,
            diffFilter: newFilter,
          };
        },
      });
    },
    [navigate],
  ); */

  const archSummary = useMemo(
    () => sanitizeArchs(builds.summary.architectures),
    [builds.summary.architectures],
  );

  const configsItems = useMemo(
    () => sanitizeConfigs(builds.summary.configs),
    [builds.summary.configs],
  );

  const buildItems = useMemo(
    () => sanitizeBuilds(builds.items),
    [builds.items],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            buildsSummary={builds.summary.builds}
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            disabled
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={builds.issues}
            failedWithUnknownIssues={builds.failedWithUnknownIssues}
          />
        </div>
        <div>
          <HardwareCommitNavigationGraph
            trees={trees}
            hardwareId={hardwareId}
          />
          <MemoizedConfigsCard
            disabled
            configs={configsItems}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <HardwareCommitNavigationGraph trees={trees} hardwareId={hardwareId} />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={builds.summary.builds}
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
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={builds.issues}
          failedWithUnknownIssues={builds.failedWithUnknownIssues}
        />
      </MobileGrid>

      <div className="flex flex-col gap-4">
        <div className="text-lg">
          <FormattedMessage id="global.builds" />
        </div>
        <HardwareDetailsBuildsTable
          buildItems={buildItems}
          hardwareId={hardwareId}
        />
      </div>
    </div>
  );
};

export default BuildTab;
