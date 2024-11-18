import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareFastResponse,
  HardwareListingResponse,
} from '@/types/hardware';

import type { TOrigins } from '@/types/general';

import http from './api';
const fetchTreeCheckoutData = async (
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

export const useHardwareListingSlow = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  {
    enabled,
  }: {
    enabled: boolean;
  },
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
      fetchTreeCheckoutData(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
      ),
    enabled,
  });
};

const fetchHardwareListingFastData = async (
  origin: TOrigins,
  startTimestampInSeconds: number,
  endTimeStampInSeconds: number,
): Promise<HardwareFastResponse> => {
  const res = await http.get('/api/hardware/', {
    params: {
      startTimestampInSeconds,
      endTimeStampInSeconds,
      mode: 'fast',
      origin,
    },
  });
  return res.data;
};

export const useHardwareListingFast = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): UseQueryResult<HardwareFastResponse> => {
  const { origin } = useSearch({ from: '/hardware' });
  const queryKey = [
    'hardwareListingFast',
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListingFastData(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
      ),
  });
};
