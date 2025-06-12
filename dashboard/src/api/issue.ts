import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { IssueListingResponse } from '@/types/issueListing';

import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import type { TFilter } from '@/types/general';
import { getTargetFilter } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchIssueListing = async ({
  intervalInDays,
  filters,
}: {
  intervalInDays?: number;
  filters: object;
}): Promise<IssueListingResponse> => {
  const backendCompatibleFilters = mapFiltersKeysToBackendCompatible(filters);
  const params = {
    interval_in_days: intervalInDays,
    ...backendCompatibleFilters,
  };

  const data = await RequestData.get<IssueListingResponse>('/api/issue/', {
    params,
  });
  return data;
};

export const useIssueListing = (
  reqFilters: TFilter,
): UseQueryResult<IssueListingResponse> => {
  const { intervalInDays } = useSearch({ from: '/_main/issues' });
  const filtersAsRecord = getTargetFilter(reqFilters, 'issueListing');

  const queryKey = ['issueTable', intervalInDays, reqFilters, filtersAsRecord];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchIssueListing({ intervalInDays, filters: { ...filtersAsRecord } }),
  });
};
