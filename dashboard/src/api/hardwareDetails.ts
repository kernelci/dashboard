import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import type { TOrigins } from '@/types/general';

import http from './api';

type fetchHardwareDetailsParams = {
  intervalInDays: number;
  origin: TOrigins;
};

const fetchHardwareDetails = async (
  hardwareId: string,
  params: fetchHardwareDetailsParams,
): Promise<THardwareDetails> => {
  const res = await http.get<THardwareDetails>(`/api/hardware/${hardwareId}`, {
    params,
  });

  return res.data;
};

export const useHardwareDetails = (
  hardwareId: string,
  intervalInDays: number,
  origin: TOrigins,
): UseQueryResult<THardwareDetails> => {
  const params = { intervalInDays, origin };
  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, params],
    queryFn: () => fetchHardwareDetails(hardwareId, params),
  });
};
