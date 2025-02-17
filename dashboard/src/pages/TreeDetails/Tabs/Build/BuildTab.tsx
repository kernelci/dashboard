import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/Builds/StatusCard';

import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/components/Tabs/TabGrid';

import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';

import {
  sanitizeArchs,
  sanitizeConfigs,
  sanitizeBuildsSummary,
  sanitizeBuilds,
} from '@/utils/utils';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import type { ISummaryItem } from '@/components/Tabs/Summary';
import type { IListingItem } from '@/components/ListingItem/ListingItem';

import {
  RedirectFrom,
  type BuildStatus,
  type TFilterObjectsKeys,
} from '@/types/general';

import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';

import type { TIssue } from '@/types/issues';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { TreeDetailsBuildsTable } from './TreeDetailsBuildsTable';

interface BuildTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
}

export interface IBuildsTab {
  architectures: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: BuildStatus;
  buildsIssues: TIssue[];
  failedBuildsWithUnknownIssues?: number;
  builds: AccordionItemBuilds[];
}

const BuildTab = ({ treeDetailsLazyLoaded }: BuildTab): JSX.Element => {
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const { diffFilter } = useSearch({
    from: '/tree/$treeId',
  });

  const { treeId } = useParams({ from: '/tree/$treeId' });

  const summaryData = treeDetailsLazyLoaded.summary?.data?.summary.builds;
  const { data: fullData, status: fullStatus } = treeDetailsLazyLoaded.full;
  const buildsData = fullData?.builds;

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

  const treeDetailsData: IBuildsTab = useMemo(
    () => ({
      architectures: sanitizeArchs(summaryData?.architectures),
      configs: sanitizeConfigs(summaryData?.configs),
      buildsSummary: sanitizeBuildsSummary(summaryData?.status),
      buildsIssues: summaryData?.issues || [],
      failedBuildsWithUnknownIssues: summaryData?.unknown_issues,
      builds: sanitizeBuilds(buildsData),
    }),
    [
      buildsData,
      summaryData?.architectures,
      summaryData?.configs,
      summaryData?.issues,
      summaryData?.status,
      summaryData?.unknown_issues,
    ],
  );
  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            buildsSummary={treeDetailsData.buildsSummary}
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
        <div>
          <TreeCommitNavigationGraph />
          <MemoizedConfigsCard
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData.buildsIssues}
          failedWithUnknownIssues={
            treeDetailsData.failedBuildsWithUnknownIssues
          }
          diffFilter={diffFilter}
          issueFilterSection="buildIssue"
          detailsId={treeId}
          pageFrom={RedirectFrom.Tree}
          issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
          extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
        />
      </DesktopGrid>
      <MobileGrid>
        <TreeCommitNavigationGraph />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={treeDetailsData.buildsSummary}
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedConfigsCard
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData.buildsIssues}
          failedWithUnknownIssues={
            treeDetailsData.failedBuildsWithUnknownIssues
          }
          diffFilter={diffFilter}
          issueFilterSection="buildIssue"
          detailsId={treeId}
          pageFrom={RedirectFrom.Tree}
          issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
          extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
        />
      </MobileGrid>

      <QuerySwitcher data={buildsData} status={fullStatus}>
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="global.builds" />
          </div>
          <TreeDetailsBuildsTable buildItems={treeDetailsData.builds} />
        </div>
      </QuerySwitcher>
    </div>
  );
};

export default BuildTab;
