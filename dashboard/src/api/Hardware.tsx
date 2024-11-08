import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareFastResponse,
  HardwareListingResponse,
} from '@/types/hardware';

import http from './api';
const fetchTreeCheckoutData = async (
  intervalInDays?: number,
): Promise<HardwareListingResponse> => {
  const res = await http.get('/api/hardware/', {
    params: { intervalInDays, mode: 'slow' },
  });
  return res.data;
};

export const useHardwareListingSlow = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<HardwareListingResponse> => {
  const {
    hardware: { intervalInDays },
  } = useSearch({ from: '/hardware' });

  const queryKey = ['hardwareListing', intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeCheckoutData(intervalInDays),
    enabled,
  });
};

const fetchHardwareListingFastData = async (
  intervalInDays?: number,
): Promise<HardwareFastResponse> => {
  const res = await http.get('/api/hardware/', {
    params: { intervalInDays, mode: 'fast' },
  });
  return res.data;
};

export const useHardwareListingFast =
  (): UseQueryResult<HardwareFastResponse> => {
    const {
      hardware: { intervalInDays },
    } = useSearch({ from: '/hardware' });
    const queryKey = ['hardwareListingFast', intervalInDays];

    return useQuery({
      queryKey,
      queryFn: () => fetchHardwareListingFastData(intervalInDays),
    });
  };
