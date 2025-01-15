import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo } from 'react';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import {
  useHardwareDetails,
  useHardwareDetailsCommitHistory,
} from '@/api/hardwareDetails';

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
      treeName: tree.treeName ?? '',
      gitRepositoryBranch: tree.gitRepositoryBranch ?? '',
      gitRepositoryUrl: tree.gitRepositoryUrl ?? '',
    });

    const result = {
      treeName: tree['treeName'] ?? '-',
      gitRepositoryBranch: tree['gitRepositoryBranch'] ?? '-',
      headGitCommitName: tree['headGitCommitName'] ?? '-',
      headGitCommitHash: tree['headGitCommitHash'] ?? '-',
      gitRepositoryUrl: tree['gitRepositoryUrl'] ?? '-',
      index: tree['index'],
      selectedCommitStatusSummary: tree['selectedCommitStatusSummary'],
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
    });
  }, [navigate]);

  const { data, status, isLoading, isPlaceholderData, error } =
    useHardwareDetails(
      hardwareId,
      startTimestampInSeconds,
      endTimestampInSeconds,
      origin,
      reqFilter,
      treeIndexes ?? [],
      treeCommits,
    );

  const hardwareTableForCommitHistory = useMemo(() => {
    const result: CommitHead[] = [];
    if (!isLoading && data) {
      data?.trees.forEach(tree => {
        const commitHead: CommitHead = {
          treeName: tree.treeName ?? '',
          repositoryUrl: tree.gitRepositoryUrl ?? '',
          branch: tree.gitRepositoryBranch ?? '',
          commitHash: tree.headGitCommitHash ?? '',
        };

        result.push(commitHead);
      });
    }
    return result;
  }, [data, isLoading]);

  const { isLoading: commitHistoryIsLoading, data: commitHistoryData } =
    useHardwareDetailsCommitHistory(
      {
        origin,
        hardwareId,
        endTimestampInSeconds,
        startTimestampInSeconds,
        commitHeads: hardwareTableForCommitHistory,
      },
      { enabled: !isLoading && !!data },
    );

  const filterListElement = useMemo(
    () => (
      <DetailsFilterList
        filter={diffFilter}
        cleanFilters={cleanAll}
        navigate={onFilterChange}
        isLoading={isPlaceholderData}
      />
    ),
    [cleanAll, diffFilter, isPlaceholderData, onFilterChange],
  );

  const startTime = getFormattedTime(startTimestampInSeconds);
  const endTime = getFormattedTime(endTimestampInSeconds);
  const startDate = getFormattedDate(startTimestampInSeconds);
  const endDate = getFormattedDate(endTimestampInSeconds);

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = data?.builds.summary.builds ?? {};
    const { statusSummary: testStatusSummary } = data?.tests ?? {};

    const { statusSummary: bootStatusSummary } = data?.boots ?? {};

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
      'global.builds': data?.builds ? (
        <BuildStatusComponent
          valid={valid}
          invalid={invalid}
          hideInconclusive
        />
      ) : (
        <></>
      ),
    };
  }, [data?.boots, data?.builds, data?.tests]);

  const treeData = useMemo(
    () =>
      prepareTreeItems({
        isCommitHistoryDataLoading: commitHistoryIsLoading,
        treeItems: data?.trees,
        commitHistoryData: commitHistoryData?.commit_history_table,
        isMainPageLoading: isPlaceholderData || isLoading,
      }),
    [
      commitHistoryIsLoading,
      data?.trees,
      commitHistoryData?.commit_history_table,
      isPlaceholderData,
      isLoading,
    ],
  );

  return (
    <QuerySwitcher
      status={status}
      data={data}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
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
              />
              {data && (
                <div className="mt-5">
                  <MemoizedCompatibleHardware
                    title={
                      <FormattedMessage id="hardwareDetails.compatibles" />
                    }
                    compatibles={data.compatibles}
                  />
                </div>
              )}
            </>
          )}
          {data && (
            <div className="flex flex-col pb-2">
              <div className="sticky top-[4.5rem] z-10">
                <div className="absolute right-0 top-2 py-4">
                  <HardwareDetailsFilter
                    paramFilter={diffFilter}
                    hardwareName={hardwareId}
                    data={data}
                    selectedTrees={treeIndexes}
                  />
                </div>
              </div>
              <HardwareDetailsTabs
                hardwareDetailsData={data}
                hardwareId={hardwareId}
                filterListElement={filterListElement}
                countElements={tabsCounts}
              />
            </div>
          )}
        </div>
      </div>
    </QuerySwitcher>
  );
}

export default HardwareDetails;
