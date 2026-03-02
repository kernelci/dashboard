import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import {
  useParams,
  useNavigate,
  useSearch,
  useRouterState,
} from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import {
  treeDetailsFromMap,
  type TreeDetailsRouteFrom,
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import MemoizedIssuesList from '@/components/Cards/IssuesList';
import { MemoizedHardwareTested } from '@/components/Cards/HardwareTested';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import { MemoizedResponsiveDetailsCards } from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';
import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';
import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { generateDiffFilter } from '@/components/Tabs/tabsUtils';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { MemoizedFilterCard } from '@/components/Cards/FilterCard';
import { sanitizeTreeinfo } from '@/utils/treeDetails';
import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';
import { getStringParam } from '@/utils/utils';

interface TestsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  urlFrom: TreeDetailsRouteFrom;
}

const TestsTab = ({
  treeDetailsLazyLoaded,
  urlFrom,
}: TestsTabProps): JSX.Element => {
  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });
  const params = useParams({ from: urlFrom });
  const { tableFilter, diffFilter, treeInfo } = useSearch({
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

  const summaryTestsData = useMemo(
    () => summaryData?.summary.tests,
    [summaryData?.summary.tests],
  );

  const { data: testsData, status: testsStatus } = useMemo(
    () => treeDetailsLazyLoaded.tests,
    [treeDetailsLazyLoaded.tests],
  );

  const fullTestsData = useMemo(() => testsData?.tests, [testsData?.tests]);

  const currentPathFilter = diffFilter.testPath
    ? Object.keys(diffFilter.testPath)[0]
    : undefined;

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
        params: params,
      });
    },
    [navigate, params],
  );

  const { treeName, branch, id } = useRouterState({
    select: s => s.location.state,
  });
  const paramsTreeName = getStringParam(params, 'treeName');
  const paramsBranch = getStringParam(params, 'branch');
  const paramsHash = getStringParam(params, 'hash');

  const stateIsSetted = treeName && branch && id;
  const stateParams = useMemo(
    () =>
      !stateIsSetted
        ? { treeName: paramsTreeName, branch: paramsBranch, id: paramsHash }
        : {},
    [stateIsSetted, paramsTreeName, paramsBranch, paramsHash],
  );

  const canGoDirect = paramsTreeName && paramsBranch && paramsHash;

  const getRowLink = useCallback(
    (bootId: string): LinkProps => {
      return canGoDirect
        ? {
            to: '/test/$testId',
            params: {
              testId: bootId,
            },
            search: s => ({
              origin: s.origin,
            }),
            state: s => ({ ...s, ...stateParams, from: RedirectFrom.Tree }),
          }
        : {
            to: '/tree/$treeId/test/$testId',
            params: {
              testId: bootId,
              treeId: sanitizedTreeInfo.hash,
            },
            search: s => ({
              origin: s.origin,
            }),
          };
    },
    [stateParams, canGoDirect, sanitizedTreeInfo],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
            },
          };
        },
        state: s => s,
        params: params,
      });
    },
    [navigate, params],
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

  const hardwareData = useMemo(() => {
    return {
      ...summaryTestsData?.environment_compatible,
      ...summaryTestsData?.environment_misc,
    };
  }, [
    summaryTestsData?.environment_compatible,
    summaryTestsData?.environment_misc,
  ]);

  const isEmptySummary = useMemo((): boolean => {
    if (!summaryTestsData) {
      return true;
    }
    return Object.values(summaryTestsData.status).every(value => value === 0);
  }, [summaryTestsData]);

  const nonEmptyData = useMemo(() => {
    if (isEmptySummary) {
      return undefined;
    } else {
      return summaryTestsData;
    }
  }, [isEmptySummary, summaryTestsData]);

  const { formatMessage } = useIntl();

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="treeDetails"
        args={{
          cmdName: 'tests',
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
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={summaryTestsData?.status}
          toggleFilterBySection={toggleFilterBySection}
          filterStatusKey="testStatus"
        />,
        <TreeCommitNavigationGraph
          key="commitGraph"
          urlFrom={urlFrom}
          treeName={sanitizedTreeInfo.treeName}
        />,
      ],
      bodyCards: [
        <MemoizedConfigList
          key="configs"
          title={<FormattedMessage id="global.configs" />}
          configStatusCounts={summaryTestsData?.configs ?? {}}
          diffFilter={diffFilter}
        />,
        <MemoizedErrorsSummary
          key="errorSummary"
          title={<FormattedMessage id="global.summary" />}
          archCompilerErrors={summaryTestsData?.architectures ?? []}
          diffFilter={diffFilter}
        />,
        <MemoizedHardwareTested
          key="hardwareTested"
          title={<FormattedMessage id="testsTab.hardwareTested" />}
          environmentCompatible={hardwareData}
          diffFilter={diffFilter}
        />,
        <MemoizedFilterCard
          cardTitle="filter.origins"
          key="origins"
          diffFilter={diffFilter}
          data={summaryTestsData?.origins ?? {}}
          filterSection="testOrigin"
        />,
        <MemoizedFilterCard
          cardTitle="filter.labs"
          key="labs"
          diffFilter={diffFilter}
          data={summaryTestsData?.labs ?? {}}
          filterSection="labs"
          hideSingleValue={false}
        />,
      ],
      footerCards: [
        <MemoizedIssuesList
          key="issues"
          title={<FormattedMessage id="global.issues" />}
          issues={summaryTestsData?.issues ?? []}
          failedWithUnknownIssues={summaryTestsData?.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="testIssue"
          detailsId={sanitizedTreeInfo.hash}
          pageFrom={RedirectFrom.Tree}
          issueExtraDetails={treeDetailsLazyLoaded.issuesExtras.data?.issues}
          extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
        />,
      ],
    };
  }, [
    diffFilter,
    hardwareData,
    sanitizedTreeInfo,
    summaryTestsData,
    toggleFilterBySection,
    treeDetailsLazyLoaded.issuesExtras,
    urlFrom,
  ]);

  return (
    <div className="pb-10">
      <QuerySwitcher
        data={nonEmptyData}
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

          <QuerySwitcher status={testsStatus} data={testsData}>
            <TestsTable
              tableKey="treeDetailsTests"
              testHistory={fullTestsData}
              onClickFilter={onClickFilter}
              filter={tableFilter.testsTable}
              getRowLink={getRowLink}
              updatePathFilter={updatePathFilter}
              currentPathFilter={currentPathFilter}
            />
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
                  tab: formatMessage({ id: 'global.tests' }).toLowerCase(),
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

export default TestsTab;
