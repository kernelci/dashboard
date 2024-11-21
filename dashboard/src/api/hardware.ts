import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { HardwareListingResponse } from '@/types/hardware';

import type { TOrigins } from '@/types/general';

import http from './api';
const fetchHardwareListing = async (
  origin: TOrigins,
  startTimestampInSeconds: number,
  endTimeStampInSeconds: number,
): Promise<HardwareListingResponse> => {
  const res = await http.get('/api/hardware/', {
    params: {
      startTimestampInSeconds,
      endTimeStampInSeconds,
      mode: 'slow',
      origin,
    },
  });
  return res.data;
};

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): UseQueryResult<HardwareListingResponse> => {
  const { origin } = useSearch({ from: '/hardware' });

  const queryKey = [
    'hardwareListing',
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListing(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
      ),
  });
};
