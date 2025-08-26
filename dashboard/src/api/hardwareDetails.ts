import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  CommitHead,
  CommitHistoryResponse,
  HardwareDetailsSummary,
  THardwareDetails,
  TTreeCommits,
} from '@/types/hardware/hardwareDetails';
import type { BuildsTabBuild, TestHistory, TFilter } from '@/types/general';
import { getTargetFilter } from '@/types/general';

import {
  isEmptyObject,
  mapFiltersKeysToBackendCompatible,
} from '@/utils/utils';

import { RequestData } from './commonRequest';

const TREE_SELECT_HEAD_VALUE = 'head';

const mapIndexesToSelectedTrees = (
  selectedIndexes: number[],
  treeIndexesLength?: number,
  treeCommits: TTreeCommits = {},
): Record<string, string> => {
  const selectedTrees: Record<string, string> = {};

  if (selectedIndexes.length === 0 && isEmptyObject(treeCommits)) {
    return selectedTrees;
  }

  const selectedArray =
    treeIndexesLength && selectedIndexes.length === 0
      ? Array.from({ length: treeIndexesLength }, (_, i) => i)
      : selectedIndexes;

  selectedArray.forEach(i => {
    const key = i.toString();
    const value = treeCommits[key] || TREE_SELECT_HEAD_VALUE;
    selectedTrees[key] = value;
  });

  return selectedTrees;
};

type HardwareDetailsVariants =
  | 'full'
  | 'builds'
  | 'boots'
  | 'tests'
  | 'summary';

type fetchHardwareDetailsBody = {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  origin: string;
  selectedCommits: Record<string, string>;
  filter?: Record<string, string[]>;
};

const fetchHardwareDetails = async <T extends HardwareDetailsVariants>({
  hardwareId,
  body,
  variant,
}: {
  hardwareId: string;
  body: fetchHardwareDetailsBody;
  variant: T;
}): Promise<HardwareDetailsResponse<T>> => {
  const urlTable: Record<HardwareDetailsVariants, string> = {
    full: `/api/hardware/${hardwareId}`,
    builds: `/api/hardware/${hardwareId}/builds`,
    boots: `/api/hardware/${hardwareId}/boots`,
    tests: `/api/hardware/${hardwareId}/tests`,
    summary: `/api/hardware/${hardwareId}/summary`,
  };

  const data = await RequestData.post<HardwareDetailsResponse<T>>(
    urlTable[variant],
    body,
  );

  return data;
};

type HardwareDetailsResponseTable = {
  full: THardwareDetails;
  summary: HardwareDetailsSummary;
  builds: BuildsTabBuild[];
  boots: TestHistory[];
  tests: TestHistory[];
};

type HardwareDetailsResponse<T extends keyof HardwareDetailsResponseTable> =
  HardwareDetailsResponseTable[T];

export type UseHardwareDetailsWithoutVariant = {
  hardwareId: string;
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  origin: string;
  filter: TFilter;
  selectedIndexes: number[];
  treeCommits: TTreeCommits;
  treeIndexesLength?: number;
  enabled?: boolean;
};

type UseHardwareDetailsParameters<T extends HardwareDetailsVariants> = {
  variant: T;
} & UseHardwareDetailsWithoutVariant;

export const useHardwareDetails = <T extends HardwareDetailsVariants>({
  hardwareId,
  startTimestampInSeconds,
  endTimestampInSeconds,
  origin,
  filter,
  selectedIndexes,
  treeCommits,
  treeIndexesLength,
  enabled = true,
  variant,
}: UseHardwareDetailsParameters<T>): UseQueryResult<
  HardwareDetailsResponse<T>
> => {
  const testFilter = getTargetFilter(filter, 'test');
  const detailsFilter = getTargetFilter(filter, 'hardwareDetails');

  const filters = {
    ...testFilter,
    ...detailsFilter,
  };

  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const selectedTrees = mapIndexesToSelectedTrees(
    selectedIndexes,
    treeIndexesLength,
    treeCommits,
  );

  const body: fetchHardwareDetailsBody = {
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    selectedCommits: selectedTrees,
    filter: filtersFormatted,
  };

  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body, variant],
    queryFn: () => fetchHardwareDetails({ hardwareId, body, variant }),
    placeholderData: previousData => previousData,
    enabled: enabled,
    refetchOnWindowFocus: false,
  }) as UseQueryResult<HardwareDetailsResponse<T>>;
};

type FetchHardwareDetailsCommitHistoryBody = {
  origin: string;
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  commitHeads: CommitHead[];
};

const fetchCommitHistory = async (
  hardwareId: string,
  body: FetchHardwareDetailsCommitHistoryBody,
): Promise<CommitHistoryResponse> => {
  const data = await RequestData.post<CommitHistoryResponse>(
    `/api/hardware/${hardwareId}/commit-history`,
    body,
  );

  return data;
};

export const useHardwareDetailsCommitHistory = (
  {
    hardwareId,
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    commitHeads,
  }: {
    hardwareId: string;
    origin: string;
    startTimestampInSeconds: number;
    endTimestampInSeconds: number;
    commitHeads: CommitHead[];
  },
  { enabled } = { enabled: true },
): UseQueryResult<CommitHistoryResponse> => {
  const body: FetchHardwareDetailsCommitHistoryBody = {
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    commitHeads,
  };

  return useQuery({
    queryKey: ['CommitHistory', hardwareId, body],
    queryFn: () => fetchCommitHistory(hardwareId, body),
    enabled,
  });
};
