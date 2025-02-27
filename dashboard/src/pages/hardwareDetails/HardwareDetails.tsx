import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { useSearchStore } from '@/hooks/store/useSearchStore';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import { useHardwareDetailsCommitHistory } from '@/api/hardwareDetails';

import type {
  CommitHead,
  CommitHistoryTable,
  PreparedTrees,
  Trees,
} from '@/types/hardware/hardwareDetails';

import MemoizedCompatibleHardware from '@/components/Cards/CompatibleHardware';

import { GroupedTestStatus } from '@/components/Status/Status';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import type { TFilter } from '@/types/general';

import { getFormattedDate, getFormattedTime } from '@/utils/date';

import { makeTreeIdentifierKey } from '@/utils/trees';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { useHardwareDetailsLazyLoadQuery } from '@/hooks/useHardwareDetailsLazyLoadQuery';

import { useQueryInconsistencyInvalidator } from '@/hooks/useQueryInconsistencyInvalidator';

import type { GroupedStatus } from '@/utils/status';
import { groupStatus, statusCountToRequiredStatusCount } from '@/utils/status';

import PageWithTitle from '@/components/PageWithTitle';

import { MemoizedTreeHardwareDetailsOGTags } from '@/components/OpenGraphTags/TreeHardwareDetailsOGTags';

import { HardwareHeader } from './HardwareDetailsHeaderTable';
import type { TreeDetailsTabRightElement } from './Tabs/HardwareDetailsTabs';
import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';
import HardwareDetailsFilter from './HardwareDetailsFilter';

const prepareTreeItems = ({
  isCommitHistoryDataLoading,
  treeItems,
  commitHistoryData,
  isMainPageLoading,
}: {
  isCommitHistoryDataLoading: boolean;
  treeItems?: Trees[];
  commitHistoryData?: CommitHistoryTable;
  isMainPageLoading: boolean;
}): PreparedTrees[] | void =>
  treeItems?.map(tree => {
    const treeIdentifier = makeTreeIdentifierKey({
      treeName: tree.tree_name ?? '',
      gitRepositoryBranch: tree.git_repository_branch ?? '',
      gitRepositoryUrl: tree.git_repository_url ?? '',
    });

    const result: PreparedTrees = {
      tree_name: tree['tree_name'] ?? '-',
      git_repository_branch: tree['git_repository_branch'] ?? '-',
      head_git_commit_name: tree['head_git_commit_name'] ?? '-',
      head_git_commit_hash: tree['head_git_commit_hash'] ?? '-',
      git_repository_url: tree['git_repository_url'] ?? '-',
      index: tree['index'],
      selected_commit_status: tree['selected_commit_status'],
      selectableCommits: commitHistoryData?.[treeIdentifier] ?? [],
      isCommitHistoryDataLoading,
      isMainPageLoading: isMainPageLoading,
    };

    return result;
  });

function HardwareDetails(): JSX.Element {
  const {
    treeIndexes,
    treeCommits,
    startTimestampInSeconds,
    endTimestampInSeconds,
    diffFilter,
    origin,
  } = useSearch({ from: '/_main/hardware/$hardwareId' });

  const { formatMessage } = useIntl();

  const { hardwareId } = useParams({ from: '/_main/hardware/$hardwareId' });
  const searchParams = useSearch({ from: '/_main/hardware/$hardwareId' });
  const updatePreviousSearch = useSearchStore(s => s.updatePreviousSearch);

  useEffect(
    () => updatePreviousSearch(searchParams),
    [searchParams, updatePreviousSearch],
  );

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const reqFilter = mapFilterToReq(diffFilter);

  const updateTreeFilters = useCallback(
    (selectedIndexes: number[]) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          treeIndexes: selectedIndexes,
        }),
        state: s => s,
      });
    },
    [navigate],
  );

  const onFilterChange = useCallback(
    (newFilter: TFilter) => {
      navigate({
        search: previousSearch => {
          return {
            ...previousSearch,
            diffFilter: newFilter,
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const cleanAll = useCallback(() => {
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: {},
        };
      },
      state: s => s,
    });
  }, [navigate]);

  const [treeIndexesLength, setTreeIndexesLength] = useState(0);
  const { summary: summaryResponse, full: fullResponse } =
    useHardwareDetailsLazyLoadQuery({
      hardwareId: hardwareId,
      startTimestampInSeconds: startTimestampInSeconds,
      endTimestampInSeconds: endTimestampInSeconds,
      origin: origin,
      filter: reqFilter,
      selectedIndexes: treeIndexes ?? [],
      treeCommits: treeCommits,
      treeIndexesLength: treeIndexesLength,
    });

  const hardwareStatusHistoryState = useRouterState({
    select: s => s.location.state.hardwareStatusCount,
  });

  type HardwareStatusComparedState = typeof hardwareStatusHistoryState;

  const hardwareDataPreparedForInconsistencyValidation: HardwareStatusComparedState =
    useMemo(() => {
      const { data } = summaryResponse;
      if (!data) {
        return;
      }

      const { boots, builds, tests } = data.summary;

      return {
        boots: statusCountToRequiredStatusCount(boots.status),
        tests: statusCountToRequiredStatusCount(tests.status),
        builds: builds.status,
      } satisfies HardwareStatusComparedState;
    }, [summaryResponse]);

  useQueryInconsistencyInvalidator<HardwareStatusComparedState>({
    referenceData: hardwareStatusHistoryState,
    comparedData: hardwareDataPreparedForInconsistencyValidation,
    navigate: navigate,
  });

  const hardwareTableForCommitHistory = useMemo(() => {
    const result: CommitHead[] = [];
    if (!summaryResponse.isLoading && summaryResponse.data) {
      summaryResponse.data.common.trees.forEach(tree => {
        const commitHead: CommitHead = {
          treeName: tree.tree_name ?? '',
          repositoryUrl: tree.git_repository_url ?? '',
          branch: tree.git_repository_branch ?? '',
          commitHash: tree.head_git_commit_hash ?? '',
        };

        result.push(commitHead);
      });
    }
    return result;
  }, [summaryResponse.data, summaryResponse.isLoading]);

  const { isLoading: commitHistoryIsLoading, data: commitHistoryData } =
    useHardwareDetailsCommitHistory(
      {
        origin,
        hardwareId,
        endTimestampInSeconds,
        startTimestampInSeconds,
        commitHeads: hardwareTableForCommitHistory,
      },
      { enabled: !fullResponse.isLoading && !!fullResponse.data },
    );

  const filterListElement = useMemo(
    () => (
      <DetailsFilterList
        filter={diffFilter}
        cleanFilters={cleanAll}
        navigate={onFilterChange}
        isLoading={summaryResponse.isPlaceholderData}
      />
    ),
    [cleanAll, diffFilter, onFilterChange, summaryResponse.isPlaceholderData],
  );

  const startTime = getFormattedTime(startTimestampInSeconds);
  const endTime = getFormattedTime(endTimestampInSeconds);
  const startDate = getFormattedDate(startTimestampInSeconds);
  const endDate = getFormattedDate(endTimestampInSeconds);

  const [buildStatusCount, bootStatusCount, testStatusCount]: [
    GroupedStatus,
    GroupedStatus,
    GroupedStatus,
  ] = useMemo(() => {
    const { status: buildStatusSummary } =
      summaryResponse.data?.summary.builds ?? {};
    const { status: testStatusSummary } =
      summaryResponse.data?.summary.tests ?? {};
    const { status: bootStatusSummary } =
      summaryResponse.data?.summary.boots ?? {};

    const buildCount = groupStatus({
      passCount: buildStatusSummary?.valid,
      failCount: buildStatusSummary?.invalid,
      nullCount: buildStatusSummary?.null,
    });

    const bootCount = groupStatus({
      passCount: bootStatusSummary?.PASS,
      failCount: bootStatusSummary?.FAIL,
      doneCount: bootStatusSummary?.DONE,
      errorCount: bootStatusSummary?.ERROR,
      missCount: bootStatusSummary?.MISS,
      skipCount: bootStatusSummary?.SKIP,
      nullCount: bootStatusSummary?.NULL,
    });

    const testCount = groupStatus({
      passCount: testStatusSummary?.PASS,
      failCount: testStatusSummary?.FAIL,
      doneCount: testStatusSummary?.DONE,
      errorCount: testStatusSummary?.ERROR,
      missCount: testStatusSummary?.MISS,
      skipCount: testStatusSummary?.SKIP,
      nullCount: testStatusSummary?.NULL,
    });

    return [buildCount, bootCount, testCount];
  }, [
    summaryResponse.data?.summary.boots,
    summaryResponse.data?.summary.builds,
    summaryResponse.data?.summary.tests,
  ]);

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    return {
      'global.tests': (
        <GroupedTestStatus
          preCalculatedGroupedStatus={testStatusCount}
          hideInconclusive
        />
      ),

      'global.boots': (
        <GroupedTestStatus
          preCalculatedGroupedStatus={bootStatusCount}
          hideInconclusive
        />
      ),

      'global.builds': (
        <GroupedTestStatus
          preCalculatedGroupedStatus={buildStatusCount}
          hideInconclusive
        />
      ),
    };
  }, [bootStatusCount, buildStatusCount, testStatusCount]);

  const treeData = useMemo(
    () =>
      prepareTreeItems({
        isCommitHistoryDataLoading: commitHistoryIsLoading,
        treeItems: summaryResponse.data?.common.trees,
        commitHistoryData: commitHistoryData?.commit_history_table,
        isMainPageLoading:
          fullResponse.isLoading || fullResponse.isPlaceholderData,
      }),
    [
      commitHistoryIsLoading,
      summaryResponse.data?.common.trees,
      commitHistoryData?.commit_history_table,
      fullResponse.isLoading,
      fullResponse.isPlaceholderData,
    ],
  );

  const hardwareTitle = useMemo(() => {
    return formatMessage(
      { id: 'title.hardwareDetails' },
      { hardwareName: hardwareId },
    );
  }, [formatMessage, hardwareId]);

  return (
    <PageWithTitle title={hardwareTitle}>
      <MemoizedTreeHardwareDetailsOGTags
        buildCount={buildStatusCount}
        bootCount={bootStatusCount}
        testCount={testStatusCount}
        title={hardwareTitle}
      />
      <QuerySwitcher
        status={summaryResponse.status}
        data={summaryResponse.data}
        customError={
          <MemoizedSectionError
            isLoading={summaryResponse.isLoading}
            errorMessage={summaryResponse.error?.message}
            emptyLabel={'global.error'}
          />
        }
      >
        <div className="flex flex-col pt-8">
          <div className="flex items-center justify-between">
            <div>
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem>
                    <BreadcrumbLink
                      to="/hardware"
                      search={previousParams => {
                        return {
                          intervalInDays: previousParams.intervalInDays,
                          origin: previousParams.origin,
                          hardwareSearch: previousParams.hardwareSearch,
                        };
                      }}
                      state={s => s}
                    >
                      <FormattedMessage id="hardware.path" />
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>
                      <span>{hardwareId}</span>
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
            <p className="text-sm font-medium text-gray-900">
              <FormattedMessage
                id="hardwareDetails.timeFrame"
                values={{
                  startDate: startDate,
                  startTime: startTime,
                  endDate: endDate,
                  endTime: endTime,
                }}
              />
            </p>
          </div>
          <div className="mt-5">
            {!!treeData && (
              <>
                <HardwareHeader
                  treeItems={treeData}
                  selectedIndexes={treeIndexes}
                  updateTreeFilters={updateTreeFilters}
                  setTreeIndexesLength={setTreeIndexesLength}
                />
                {summaryResponse.data &&
                  summaryResponse.data.common.compatibles.length > 0 && (
                    <div className="mt-5">
                      <MemoizedCompatibleHardware
                        title={<FormattedMessage id="global.compatibles" />}
                        compatibles={summaryResponse.data.common.compatibles}
                        diffFilter={diffFilter}
                      />
                    </div>
                  )}
              </>
            )}
            <div className="flex flex-col pb-2">
              <div className="sticky top-[4.5rem] z-10">
                <div className="absolute top-2 right-0 py-4">
                  <HardwareDetailsFilter
                    paramFilter={diffFilter}
                    hardwareName={hardwareId}
                    data={summaryResponse.data}
                    selectedTrees={treeIndexes}
                  />
                </div>
              </div>
              {summaryResponse.data && (
                <HardwareDetailsTabs
                  hardwareId={hardwareId}
                  filterListElement={filterListElement}
                  countElements={tabsCounts}
                  summaryData={summaryResponse.data}
                  fullDataResult={fullResponse}
                />
              )}
            </div>
          </div>
        </div>
      </QuerySwitcher>
    </PageWithTitle>
  );
}

export default HardwareDetails;
