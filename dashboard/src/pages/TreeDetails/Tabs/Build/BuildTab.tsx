import { FormattedMessage, useIntl } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';

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

import { RedirectFrom } from '@/types/general';
import type { RequiredStatusCount, TFilterObjectsKeys } from '@/types/general';

import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';

import type { TIssue } from '@/types/issues';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { TreeDetailsBuildsTable } from './TreeDetailsBuildsTable';

interface BuildTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
}

export interface IBuildsTab {
  architectures: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: RequiredStatusCount;
  buildsIssues: TIssue[];
  failedBuildsWithUnknownIssues?: number;
  builds: AccordionItemBuilds[];
}

const BuildTab = ({ treeDetailsLazyLoaded }: BuildTab): JSX.Element => {
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const { diffFilter } = useSearch({
    from: '/_main/tree/$treeId',
  });

  const { treeId } = useParams({ from: '/_main/tree/$treeId' });

  const {
    data: summaryData,
    status: summaryStatus,
    error: summaryError,
    isLoading: summaryIsLoading,
  } = useMemo(
    () => treeDetailsLazyLoaded.summary,
    [treeDetailsLazyLoaded.summary],
  );

  const summaryBuildsData = useMemo(
    () => summaryData?.summary.builds,
    [summaryData?.summary.builds],
  );

  const {
    data: fullData,
    status: fullStatus,
    error: fullError,
    isLoading: fullIsLoading,
  } = useMemo(() => treeDetailsLazyLoaded.full, [treeDetailsLazyLoaded.full]);

  const fullBuildsData = useMemo(() => fullData?.builds, [fullData?.builds]);

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
      architectures: sanitizeArchs(summaryBuildsData?.architectures),
      configs: sanitizeConfigs(summaryBuildsData?.configs),
      buildsSummary: sanitizeBuildsSummary(summaryBuildsData?.status),
      buildsIssues: summaryBuildsData?.issues || [],
      failedBuildsWithUnknownIssues: summaryBuildsData?.unknown_issues,
      builds: sanitizeBuilds(fullBuildsData),
    }),
    [
      fullBuildsData,
      summaryBuildsData?.architectures,
      summaryBuildsData?.configs,
      summaryBuildsData?.issues,
      summaryBuildsData?.status,
      summaryBuildsData?.unknown_issues,
    ],
  );

  const isEmptySummary = useMemo((): boolean => {
    if (!summaryBuildsData) {
      return true;
    }
    return Object.values(summaryBuildsData.status).every(value => value === 0);
  }, [summaryBuildsData]);

  const { formatMessage } = useIntl();

  return (
    <div>
      <QuerySwitcher
        data={summaryData}
        status={summaryStatus}
        skeletonClassname="max-h-[100px]"
        customError={
          <MemoizedSectionError
            isLoading={summaryIsLoading}
            errorMessage={summaryError?.message}
            forceErrorMessageUse
            variant="warning"
          />
        }
      >
        <div className="flex flex-col gap-8 pt-4">
          <DesktopGrid>
            <div>
              <MemoizedStatusCard
                title={<FormattedMessage id="buildTab.buildStatus" />}
                toggleFilterBySection={toggleFilterBySection}
                statusCounts={treeDetailsData.buildsSummary}
                filterStatusKey="buildStatus"
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
              issueExtraDetails={
                treeDetailsLazyLoaded.issuesExtras.data?.issues
              }
              extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
            />
          </DesktopGrid>
          <MobileGrid>
            <TreeCommitNavigationGraph />
            <MemoizedStatusCard
              title={<FormattedMessage id="buildTab.buildStatus" />}
              toggleFilterBySection={toggleFilterBySection}
              statusCounts={treeDetailsData.buildsSummary}
              filterStatusKey="buildStatus"
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
              issueExtraDetails={
                treeDetailsLazyLoaded.issuesExtras.data?.issues
              }
              extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
            />
          </MobileGrid>

          <QuerySwitcher
            data={fullBuildsData}
            status={fullStatus}
            customError={
              <MemoizedSectionError
                isLoading={fullIsLoading}
                errorMessage={fullError?.message}
                emptyLabel={'global.error'}
              />
            }
          >
            <div className="flex flex-col gap-4">
              <div className="text-lg">
                <FormattedMessage id="global.builds" />
              </div>
              <TreeDetailsBuildsTable buildItems={treeDetailsData.builds} />
            </div>
          </QuerySwitcher>
        </div>
      </QuerySwitcher>
      {isEmptySummary && (
        <div className="mx-48 max-2xl:mx-0">
          {summaryError !== null && (
            <div className="px-4 pb-2">
              <FormattedMessage
                id="tab.findOnPreviousCheckoutsTooltip"
                values={{
                  tab: formatMessage({ id: 'global.builds' }).toLowerCase(),
                }}
              />
            </div>
          )}
          <TreeCommitNavigationGraph />
        </div>
      )}
    </div>
  );
};

export default BuildTab;
