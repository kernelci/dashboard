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
  intervalInDays?: number,
): Promise<HardwareListingResponse> => {
  const res = await http.get('/api/hardware/', {
    params: { intervalInDays, mode: 'slow', origin },
  });
  return res.data;
};

export const useHardwareListingSlow = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<HardwareListingResponse> => {
  const { intervalInDays, origin } = useSearch({ from: '/hardware' });

  const queryKey = ['hardwareListing', intervalInDays, origin];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeCheckoutData(origin, intervalInDays),
    enabled,
  });
};

const fetchHardwareListingFastData = async (
  origin: TOrigins,
  intervalInDays?: number,
): Promise<HardwareFastResponse> => {
  const res = await http.get('/api/hardware/', {
    params: { intervalInDays, mode: 'fast', origin },
  });
  return res.data;
};

export const useHardwareListingFast =
  (): UseQueryResult<HardwareFastResponse> => {
    const { intervalInDays, origin } = useSearch({ from: '/hardware' });
    const queryKey = ['hardwareListingFast', intervalInDays, origin];

    return useQuery({
      queryKey,
      queryFn: () => fetchHardwareListingFastData(origin, intervalInDays),
    });
  };
