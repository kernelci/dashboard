import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { LabListingResponse } from '@/types/lab';

import type { LabsListingRoutesMap } from '@/utils/constants/labsListing';

import { RequestData } from './commonRequest';

const fetchLabsListing = async (
  origin: string,
  intervalInDays: number,
): Promise<LabListingResponse> => {
  return RequestData.get<LabListingResponse>('/api/labs/', {
    params: {
      origin,
      interval_in_days: intervalInDays,
    },
  });
};

export const useLabsListing = (
  searchFrom: LabsListingRoutesMap['search'],
): UseQueryResult<LabListingResponse> => {
  const { origin, intervalInDays } = useSearch({ from: searchFrom });

  return useQuery({
    queryKey: ['labsListing', origin, intervalInDays],
    queryFn: () => fetchLabsListing(origin, intervalInDays),
    refetchOnWindowFocus: false,
  });
};
