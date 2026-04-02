import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { IssueListingResponse } from '@/types/issueListing';

import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import type { TFilter } from '@/types/general';
import { getTargetFilter } from '@/types/general';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import { RequestData } from './commonRequest';

const getDefaultEndTimestamp = (): number =>
  dateObjectToTimestampInSeconds(new Date());

export const fetchIssueListing = async ({
  startTimestampInSeconds,
  endTimestampInSeconds,
  filters,
}: {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  filters: object;
}): Promise<IssueListingResponse> => {
  const backendCompatibleFilters = mapFiltersKeysToBackendCompatible(filters);
  const params = {
    startTimestampInSeconds,
    endTimestampInSeconds,
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
  const { startTimestampInSeconds, endTimestampInSeconds } = useSearch({
    from: '/_main/issues',
  });
  const filtersAsRecord = getTargetFilter(reqFilters, 'issueListing');

  const endTs = endTimestampInSeconds ?? getDefaultEndTimestamp();
  const startTs =
    startTimestampInSeconds ?? endTs - daysToSeconds(REDUCED_TIME_SEARCH);

  const queryKey = ['issueTable', startTs, endTs, reqFilters, filtersAsRecord];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchIssueListing({
        startTimestampInSeconds: startTs,
        endTimestampInSeconds: endTs,
        filters: { ...filtersAsRecord },
      }),
  });
};
