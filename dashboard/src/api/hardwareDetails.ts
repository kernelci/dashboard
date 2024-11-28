import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  THardwareDetails,
  THardwareDetailsFilter,
} from '@/types/hardware/hardwareDetails';
import { getTargetFilter } from '@/types/hardware/hardwareDetails';
import type { TOrigins } from '@/types/general';

import http from './api';

type fetchHardwareDetailsBody = {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
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

const mapIndexesToSelectedTrees = (
  selectedIndexes: number[],
): Record<number, string> => {
  return Object.fromEntries(
    Array.from(selectedIndexes, index => [index.toString(), 'selected']),
  );
};

export const useHardwareDetails = (
  hardwareId: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  origin: TOrigins,
  filter: { [key: string]: string[] },
  selectedIndexes: number[],
): UseQueryResult<THardwareDetails> => {
  const detailsFilter = getTargetFilter(filter, 'hardwareDetails');
  const filtersFormatted = mapFiltersKeysToBackendCompatible(detailsFilter);

  const selectedTrees = mapIndexesToSelectedTrees(selectedIndexes);

  const body: fetchHardwareDetailsBody = {
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    selectedTrees,
    filter: filtersFormatted,
  };

  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body],
    queryFn: () => fetchHardwareDetails(hardwareId, body),
    placeholderData: previousData => previousData,
  });
};
