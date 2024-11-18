import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import type { TOrigins } from '@/types/general';

import http from './api';

type fetchHardwareDetailsBody = {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  origin: TOrigins;
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

export const useHardwareDetails = (
  hardwareId: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  origin: TOrigins,
): UseQueryResult<THardwareDetails> => {
  const body = { origin, startTimestampInSeconds, endTimestampInSeconds };
  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, body],
    queryFn: () => fetchHardwareDetails(hardwareId, body),
  });
};
