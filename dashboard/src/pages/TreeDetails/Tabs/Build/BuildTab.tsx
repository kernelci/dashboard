import { FormattedMessage } from 'react-intl';

import { useCallback } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { TFilterObjectsKeys } from '@/types/tree/TreeDetails';
import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/Builds/StatusCard';

import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/components/Tabs/TabGrid';

import { TreeDetailsBuildsTable } from './TreeDetailsBuildsTable';

interface BuildTab {
  treeDetailsData: ITreeDetails;
}

const BuildTab = ({ treeDetailsData }: BuildTab): JSX.Element => {
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const {
    diffFilter,
  }: { diffFilter: Record<string, Record<string, boolean>> } = useSearch({
    from: '/tree/$treeId/',
  });

  const toggleFilterBySection = useCallback(
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
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard<TFilterObjectsKeys>
            toggleFilterBySection={toggleFilterBySection}
            buildsSummary={treeDetailsData.buildsSummary}
          />
          <MemoizedErrorsSummaryBuild<TFilterObjectsKeys>
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={treeDetailsData.issues || []}
          />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedConfigsCard<TFilterObjectsKeys>
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <CommitNavigationGraph />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={treeDetailsData.buildsSummary}
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild<TFilterObjectsKeys>
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
          <MemoizedConfigsCard<TFilterObjectsKeys>
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
            diffFilter={diffFilter}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData.issues}
        />
      </MobileGrid>

      {treeDetailsData && (
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="treeDetails.builds" />
          </div>

          <TreeDetailsBuildsTable buildItems={treeDetailsData.builds} />
        </div>
      )}
    </div>
  );
};

export default BuildTab;
