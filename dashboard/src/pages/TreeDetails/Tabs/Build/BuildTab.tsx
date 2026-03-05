import { FormattedMessage, useIntl } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';

import { MemoizedConfigsCard } from '@/components/Tabs/Builds/ConfigsCard';

import { MemoizedErrorsSummaryBuild } from '@/components/Tabs/Builds/BuildCards';

import { MemoizedResponsiveDetailsCards } from '@/components/Tabs/TabGrid';

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

import {
  treeDetailsFromMap,
  type AccordionItemBuilds,
  type TreeDetailsRouteFrom,
} from '@/types/tree/TreeDetails';

import type { TIssue } from '@/types/issues';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { MemoizedFilterCard } from '@/components/Cards/FilterCard';
import { sanitizeTreeinfo } from '@/utils/treeDetails';
import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { TreeDetailsBuildsTable } from './TreeDetailsBuildsTable';

interface BuildTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  urlFrom: TreeDetailsRouteFrom;
}

interface IBuildsTab {
  architectures: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: RequiredStatusCount;
  buildsIssues: TIssue[];
  failedBuildsWithUnknownIssues?: number;
  builds: AccordionItemBuilds[];
  origins: Record<string, RequiredStatusCount>;
  labs: Record<string, RequiredStatusCount>;
}

const BuildTab = ({
  treeDetailsLazyLoaded,
  urlFrom,
}: BuildTab): JSX.Element => {
  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });
  const params = useParams({ from: urlFrom });
  const { diffFilter, treeInfo } = useSearch({
    from: urlFrom,
  });

  const sanitizedTreeInfo = useMemo(() => {
    return sanitizeTreeinfo({
      params,
      treeInfo,
      urlFrom,
      summaryUrl: treeDetailsLazyLoaded.summary.data?.common.tree_url,
    });
  }, [
    params,
    treeDetailsLazyLoaded.summary.data?.common.tree_url,
    treeInfo,
    urlFrom,
  ]);

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
    data: buildsData,
    status: buildsStatus,
    error: buildsError,
    isLoading: buildsIsLoading,
  } = useMemo(
    () => treeDetailsLazyLoaded.builds,
    [treeDetailsLazyLoaded.builds],
  );

  const fullBuildsData = useMemo(
    () => buildsData?.builds,
    [buildsData?.builds],
  );

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
        params: params,
      });
    },
    [navigate, params],
  );

  const treeDetailsData: IBuildsTab = useMemo(
    () => ({
      architectures: sanitizeArchs(summaryBuildsData?.architectures),
      configs: sanitizeConfigs(summaryBuildsData?.configs),
      buildsSummary: sanitizeBuildsSummary(summaryBuildsData?.status),
      buildsIssues: summaryBuildsData?.issues || [],
      failedBuildsWithUnknownIssues: summaryBuildsData?.unknown_issues,
      builds: sanitizeBuilds(fullBuildsData),
      origins: summaryBuildsData?.origins || {},
      labs: summaryBuildsData?.labs || {},
    }),
    [
      fullBuildsData,
      summaryBuildsData?.architectures,
      summaryBuildsData?.configs,
      summaryBuildsData?.issues,
      summaryBuildsData?.origins,
      summaryBuildsData?.status,
      summaryBuildsData?.unknown_issues,
      summaryBuildsData?.labs,
    ],
  );

  const isEmptySummary = useMemo((): boolean => {
    if (!summaryBuildsData) {
      return true;
    }
    return Object.values(summaryBuildsData.status).every(value => value === 0);
  }, [summaryBuildsData]);

  const { formatMessage } = useIntl();

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="treeDetails"
        args={{
          cmdName: 'builds',
          'git-url': sanitizedTreeInfo.gitUrl,
          branch: sanitizedTreeInfo.gitBranch,
          commit: sanitizedTreeInfo.hash,
        }}
      />
    ),
    [
      sanitizedTreeInfo.gitBranch,
      sanitizedTreeInfo.gitUrl,
      sanitizedTreeInfo.hash,
    ],
  );

  const { topCards, bodyCards, footerCards } = useMemo(() => {
    return {
      topCards: [
        <MemoizedStatusCard
          key="statusGraph"
          title={<FormattedMessage id="buildTab.buildStatus" />}
          toggleFilterBySection={toggleFilterBySection}
          statusCounts={treeDetailsData.buildsSummary}
          filterStatusKey="buildStatus"
        />,
        <TreeCommitNavigationGraph
          key="commitGraph"
          urlFrom={urlFrom}
          treeName={sanitizedTreeInfo.treeName}
        />,
      ],
      bodyCards: [
        <MemoizedErrorsSummaryBuild
          key="errorsSummary"
          summaryBody={treeDetailsData.architectures}
          toggleFilterBySection={toggleFilterBySection}
          diffFilter={diffFilter}
        />,
        <MemoizedFilterCard
          cardTitle="filter.origins"
          key="origins"
          diffFilter={diffFilter}
          data={treeDetailsData.origins}
          filterSection="buildOrigin"
        />,
        <MemoizedConfigsCard
          key="configs"
          configs={treeDetailsData.configs}
          toggleFilterBySection={toggleFilterBySection}
          diffFilter={diffFilter}
        />,
      ],
      footerCards: [
        <MemoizedIssuesList
          key="issues"
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData.buildsIssues}
          failedWithUnknownIssues={
            treeDetailsData.failedBuildsWithUnknownIssues
          }
          diffFilter={diffFilter}
          issueFilterSection="buildIssue"
          detailsId={sanitizedTreeInfo.hash}
          pageFrom={RedirectFrom.Tree}
          issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
          extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
        />,
      ],
    };
  }, [
    diffFilter,
    sanitizedTreeInfo,
    toggleFilterBySection,
    treeDetailsData,
    treeDetailsLazyLoaded.issuesExtras,
    urlFrom,
  ]);

  return (
    <div className="pb-10">
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
          <MemoizedResponsiveDetailsCards
            topCards={topCards}
            bodyCards={bodyCards}
            footerCards={footerCards}
          />

          <QuerySwitcher
            data={fullBuildsData}
            status={buildsStatus}
            customError={
              <MemoizedSectionError
                isLoading={buildsIsLoading}
                errorMessage={buildsError?.message}
                emptyLabel={'global.error'}
              />
            }
          >
            <div className="flex flex-col gap-4">
              <div className="text-lg">
                <FormattedMessage id="global.builds" />
              </div>
              <TreeDetailsBuildsTable
                buildItems={treeDetailsData.builds}
                urlFrom={urlFrom}
              />
            </div>
          </QuerySwitcher>
          {kcidevComponent}
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
          <TreeCommitNavigationGraph
            urlFrom={urlFrom}
            treeName={sanitizedTreeInfo.treeName}
          />
        </div>
      )}
    </div>
  );
};

export default BuildTab;
