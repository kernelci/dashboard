import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { LabListingResponse } from '@/types/lab';

import type { LabsListingRoutesMap } from '@/utils/constants/labsListing';

import { RequestData } from './commonRequest';

const fetchLabsListing = async (
  intervalInDays: number,
): Promise<LabListingResponse> => {
  return RequestData.get<LabListingResponse>('/api/labs/', {
    params: {
      interval_in_days: intervalInDays,
    },
  });
};

export const useLabsListing = (
  searchFrom: LabsListingRoutesMap['search'],
): UseQueryResult<LabListingResponse> => {
  const { intervalInDays } = useSearch({ from: searchFrom });

  return useQuery({
    queryKey: ['labsListing', intervalInDays],
    queryFn: () => fetchLabsListing(intervalInDays),
    refetchOnWindowFocus: false,
  });
};
