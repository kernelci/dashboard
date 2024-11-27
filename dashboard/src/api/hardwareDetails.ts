import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  THardwareDetails,
  THardwareDetailsFilter,
  TTreeCommits,
} from '@/types/hardware/hardwareDetails';
import { getTargetFilter } from '@/types/hardware/hardwareDetails';
import type { TOrigins } from '@/types/general';

import http from './api';

type fetchHardwareDetailsBody = {
  limitTimestampInSeconds: number;
  origin: TOrigins;
  selectedTrees: Record<string, string>;
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
  const res = await http.post<THardwareDetails>(
    `/api/hardware/${hardwareId}`,
    body,
  );

  return res.data;
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
  limitTimestampInSeconds: number,
  origin: TOrigins,
  filter: { [key: string]: string[] },
  selectedIndexes: number[],
  treeCommits: TTreeCommits,
): UseQueryResult<THardwareDetails> => {
  const detailsFilter = getTargetFilter(filter, 'hardwareDetails');
  const filtersFormatted = mapFiltersKeysToBackendCompatible(detailsFilter);
  const selectedTrees = mapIndexesToSelectedTrees(selectedIndexes, treeCommits);

  const body: fetchHardwareDetailsBody = {
    origin,
    limitTimestampInSeconds,
    selectedTrees,
    filter: filtersFormatted,
  };

  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body],
    queryFn: () => fetchHardwareDetails(hardwareId, body),
  });
};
