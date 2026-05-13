import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareListingResponse,
  HardwareListingResponseV2,
} from '@/types/hardware';

import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

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
  searchFrom: HardwareListingRoutesMap['v1']['search'],
): UseQueryResult<HardwareListingResponse> => {
  const { origin } = useSearch({ from: searchFrom });

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

const fetchHardwareListingV2 = async (
  origin: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  commitsList?: string[],
): Promise<HardwareListingResponseV2> => {
  const data = await RequestData.get<HardwareListingResponseV2>(
    '/api/hardware-v2/',
    {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        origin,
        ...(commitsList?.length ? { commitsList: commitsList.join(',') } : {}),
      },
    },
  );

  return data;
};

export const useHardwareListingV2 = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  searchFrom: HardwareListingRoutesMap['v2']['search'],
  commitsList?: string[],
): UseQueryResult<HardwareListingResponseV2> => {
  const { origin } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListingV2',
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
    commitsList ?? null,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListingV2(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
        commitsList,
      ),
    refetchOnWindowFocus: false,
  });
};
