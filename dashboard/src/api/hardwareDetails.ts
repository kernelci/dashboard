import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import http from './api';

const fetchHardwareDetails = async (
  hardwareId: string,
  daysInterval: number,
): Promise<THardwareDetails> => {
  const params = { daysInterval };
  const res = await http.get<THardwareDetails>(`/api/hardware/${hardwareId}`, {
    params,
  });

  return res.data;
};

export const useHardwareDetails = (
  hardwareId: string,
  daysInterval: number,
): UseQueryResult<THardwareDetails> => {
  return useQuery({
    queryKey: ['HardwareDetails', hardwareId, daysInterval],
    queryFn: () => fetchHardwareDetails(hardwareId, daysInterval),
  });
};
