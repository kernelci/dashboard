import { FormattedMessage } from 'react-intl';

import { useMemo } from 'react';

import { MemoizedErrorsSummaryBuild } from '@/pages/TreeDetails/Tabs/BuildCards';

import {
  MemoizedConfigsCard,
  MemoizedStatusCard,
} from '@/pages/TreeDetails/Tabs/Build/BuildTab';
import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';
import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import { sanitizeArchs, sanitizeBuilds, sanitizeConfigs } from '@/utils/utils';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { HardwareDetailsBuildsTable } from './HardwareDetailsBuildsTable';

interface TBuildTab {
  builds: THardwareDetails['builds'];
  hardwareId: string;
}

const toggleFilterBySection = console.error;

const BuildTab = ({ builds, hardwareId }: TBuildTab): JSX.Element => {
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
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={builds.issues}
          />
        </div>
        <MemoizedConfigsCard
          configs={configsItems}
          toggleFilterBySection={toggleFilterBySection}
        />
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={builds.summary.builds}
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedConfigsCard
            configs={configsItems}
            toggleFilterBySection={toggleFilterBySection}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={builds.issues}
        />
      </MobileGrid>

      <div className="flex flex-col gap-4">
        <div className="text-lg">
          <FormattedMessage id="global.build" />
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
