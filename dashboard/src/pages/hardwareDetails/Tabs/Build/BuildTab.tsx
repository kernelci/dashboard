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

import { MemoizedResponsiveDetailsCards } from '@/components/Tabs/TabGrid';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';
import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';
import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';

import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';

import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { MemoizedFilterCard } from '@/components/Cards/FilterCard';

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

  const { diffFilter, origin } = useSearch({
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

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="hardwareDetails"
        args={{
          cmdName: 'hardware builds',
          name: hardwareId,
          origin: origin,
          json: true,
        }}
      />
    ),
    [hardwareId, origin],
  );

  const { topCards, bodyCards, footerCards } = useMemo(() => {
    return {
      topCards: [
        <MemoizedStatusCard
          key="statusGraph"
          title={<FormattedMessage id="buildTab.buildStatus" />}
          toggleFilterBySection={toggleFilterBySection}
          statusCounts={buildsSummary.status}
          filterStatusKey="buildStatus"
        />,
        <HardwareCommitNavigationGraph
          key="commitGraph"
          trees={trees}
          hardwareId={hardwareId}
        />,
      ],
      bodyCards: [
        <MemoizedErrorsSummaryBuild
          key="errorsSummary"
          summaryBody={archSummary}
          toggleFilterBySection={toggleFilterBySection}
          diffFilter={diffFilter}
        />,
        <MemoizedConfigsCard
          key="configs"
          configs={configsItems}
          toggleFilterBySection={toggleFilterBySection}
          diffFilter={diffFilter}
        />,
        <MemoizedFilterCard
          cardTitle="filter.labs"
          key="labs"
          diffFilter={diffFilter}
          data={buildsSummary.labs}
          filterSection="buildLab"
          hideSingleValue={false}
        />,
      ],
      footerCards: [
        <MemoizedIssuesList
          key="issues"
          title={<FormattedMessage id="global.issues" />}
          issues={buildsSummary.issues}
          failedWithUnknownIssues={buildsSummary.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="buildIssue"
          detailsId={hardwareId}
          pageFrom={RedirectFrom.Hardware}
        />,
      ],
    };
  }, [
    archSummary,
    buildsSummary,
    configsItems,
    diffFilter,
    hardwareId,
    toggleFilterBySection,
    trees,
  ]);

  return (
    <div className="flex flex-col gap-8 pt-4 pb-10">
      <MemoizedResponsiveDetailsCards
        topCards={topCards}
        bodyCards={bodyCards}
        footerCards={footerCards}
      />

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
        {kcidevComponent}
      </div>
    </div>
  );
};

export default BuildTab;
