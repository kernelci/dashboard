import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import http from './api';

const fetchHardwareDetails = async (
  hardwareId: string,
  intervalInDays: number,
): Promise<THardwareDetails> => {
  const params = { intervalInDays };
  const res = await http.get<THardwareDetails>(`/api/hardware/${hardwareId}`, {
    params,
  });

  return res.data;
};

export const useHardwareDetails = (
  hardwareId: string,
  intervalInDays: number,
): UseQueryResult<THardwareDetails> => {
  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, intervalInDays],
    queryFn: () => fetchHardwareDetails(hardwareId, intervalInDays),
  });
};
