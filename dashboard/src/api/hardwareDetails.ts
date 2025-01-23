import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  CommitHead,
  CommitHistoryResponse,
  CommitHistoryTable,
  THardwareDetails,
  THardwareDetailsFilter,
  TTreeCommits,
} from '@/types/hardware/hardwareDetails';
import type { TFilter, TOrigins } from '@/types/general';
import { getTargetFilter } from '@/types/general';

import { RequestData } from './commonRequest';

type fetchHardwareDetailsBody = {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  origin: TOrigins;
  selectedCommits: Record<string, string>;
  filter?: Record<string, string[]>;
};

const mapFiltersKeysToBackendCompatible = (
  filter: THardwareDetailsFilter | Record<string, never>,
): Record<string, string[]> => {
  const filterParam: { [key: string]: string[] } = {};

  Object.keys(filter).forEach(key => {
    const filterList = filter[key as keyof THardwareDetailsFilter];
    filterList?.forEach(value => {
      if (!filterParam[`filter_${key}`])
        filterParam[`filter_${key}`] = [value.toString()];
      else filterParam[`filter_${key}`].push(value.toString());
    });
  });

  return filterParam;
};

const fetchHardwareDetails = async (
  hardwareId: string,
  body: fetchHardwareDetailsBody,
): Promise<THardwareDetails> => {
  const data = await RequestData.post<THardwareDetails>(
    `/api/hardware/${hardwareId}`,
    body,
  );

  return data;
};

const TREE_SELECT_HEAD_VALUE = 'head';

const mapIndexesToSelectedTrees = (
  selectedIndexes: number[],
  treeCommits: TTreeCommits = {},
): Record<string, string> => {
  const selectedTrees: Record<string, string> = {};

  selectedIndexes.forEach(idx => {
    const key = idx.toString();
    const value = treeCommits[key] || TREE_SELECT_HEAD_VALUE;
    selectedTrees[key] = value;
  });

  return selectedTrees;
};

export const useHardwareDetails = (
  hardwareId: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  origin: TOrigins,
  filter: TFilter,
  selectedIndexes: number[],
  treeCommits: TTreeCommits,
): UseQueryResult<THardwareDetails> => {
  const testFilter = getTargetFilter(filter, 'test');
  const detailsFilter = getTargetFilter(filter, 'hardwareDetails');

  const filters = {
    ...testFilter,
    ...detailsFilter,
  };

  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const selectedTrees = mapIndexesToSelectedTrees(selectedIndexes, treeCommits);

  const body: fetchHardwareDetailsBody = {
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    selectedCommits: selectedTrees,
    filter: filtersFormatted,
  };

  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body],
    queryFn: () => fetchHardwareDetails(hardwareId, body),
    placeholderData: previousData => previousData,
  });
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
): Promise<CommitHistoryTable> => {
  const data = await RequestData.post<CommitHistoryTable>(
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
