import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { HardwareListingResponse } from '@/types/hardware';

import { RequestData } from './commonRequest';

const fetchHardwareListing = async (
  origin: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingResponse>(
    '/api/hardware/',
    {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        origin,
      },
    },
  );

  return data;
};

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): UseQueryResult<HardwareListingResponse> => {
  const { origin } = useSearch({ from: '/_main/hardware' });

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
    refetchOnWindowFocus: false,
  });
};
