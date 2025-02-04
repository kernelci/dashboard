import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, useState } from 'react';

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

import {
  GroupedTestStatus,
  BuildStatus as BuildStatusComponent,
} from '@/components/Status/Status';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import type { TFilter } from '@/types/general';

import { getFormattedDate, getFormattedTime } from '@/utils/date';

import { makeTreeIdentifierKey } from '@/utils/trees';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { useHardwareDetailsLazyLoadQuery } from '@/hooks/useHardwareDetailsLazyLoadQuery';

import { useQueryInconsistencyInvalidator } from '@/hooks/useQueryInconsistencyInvalidator';

import { statusCountToRequiredStatusCount } from '@/utils/status';

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
  } = useSearch({ from: '/hardware/$hardwareId' });

  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });

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
      if (!data) return;

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

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { status: buildStatusSummary } =
      summaryResponse.data?.summary.builds ?? {};
    const { status: testStatusSummary } =
      summaryResponse.data?.summary.tests ?? {};
    const { status: bootStatusSummary } =
      summaryResponse.data?.summary.boots ?? {};

    return {
      'global.tests': testStatusSummary ? (
        <GroupedTestStatus
          fail={testStatusSummary.FAIL}
          pass={testStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.boots': bootStatusSummary ? (
        <GroupedTestStatus
          fail={bootStatusSummary.FAIL}
          pass={bootStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.builds': buildStatusSummary ? (
        <BuildStatusComponent
          valid={buildStatusSummary.valid}
          invalid={buildStatusSummary.invalid}
          hideInconclusive
        />
      ) : (
        <></>
      ),
    };
  }, [
    summaryResponse.data?.summary.boots,
    summaryResponse.data?.summary.builds,
    summaryResponse.data?.summary.tests,
  ]);

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

  return (
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
                      title={
                        <FormattedMessage id="hardwareDetails.compatibles" />
                      }
                      compatibles={summaryResponse.data.common.compatibles}
                      diffFilter={diffFilter}
                    />
                  </div>
                )}
            </>
          )}
          <div className="flex flex-col pb-2">
            <div className="sticky top-[4.5rem] z-10">
              <div className="absolute right-0 top-2 py-4">
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
  );
}

export default HardwareDetails;
