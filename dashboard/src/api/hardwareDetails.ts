import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import type { TOrigins } from '@/types/general';

import http from './api';

type fetchHardwareDetailsBody = {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  origin: TOrigins;
  selectedTrees: Record<string, string>;
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
  selectedIndexes: number[],
): UseQueryResult<THardwareDetails> => {
  const selectedTrees = mapIndexesToSelectedTrees(selectedIndexes);

  const body: fetchHardwareDetailsBody = {
    origin,
    startTimestampInSeconds,
    endTimestampInSeconds,
    selectedTrees,
  };

  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body],
    queryFn: () => fetchHardwareDetails(hardwareId, body),
  });
};
