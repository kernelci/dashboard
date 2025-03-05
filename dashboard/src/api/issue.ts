import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { IssueListingResponse } from '@/types/issueListing';

import { RequestData } from './commonRequest';

const fetchIssueListing = async (
  origin: string,
  intervalInDays?: number,
): Promise<IssueListingResponse> => {
  const data = await RequestData.get<IssueListingResponse>('/api/issue/', {
    params: { origin, intervalInDays },
  });
  return data;
};

export const useIssueListing = (): UseQueryResult<IssueListingResponse> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/issues' });

  const queryKey = ['issueTable', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchIssueListing(origin, intervalInDays),
  });
};
