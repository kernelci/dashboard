import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { IssueListingResponse } from '@/types/issueListing';

import { RequestData } from './commonRequest';

type IssueListingParams = {
  intervalInDays?: number;
  culpritCode?: boolean;
  culpritHarness?: boolean;
  culpritTool?: boolean;
};

const fetchIssueListing = async (
  intervalInDays?: number,
  culpritCode?: boolean,
  culpritHarness?: boolean,
  culpritTool?: boolean,
): Promise<IssueListingResponse> => {
  const params: IssueListingParams = { intervalInDays };

  if (culpritCode) {
    params['culpritCode'] = true;
  }
  if (culpritHarness) {
    params['culpritHarness'] = true;
  }
  if (culpritTool) {
    params['culpritTool'] = true;
  }

  const data = await RequestData.get<IssueListingResponse>('/api/issue/', {
    params,
  });
  return data;
};

export const useIssueListing = (): UseQueryResult<IssueListingResponse> => {
  const { intervalInDays, culpritCode, culpritHarness, culpritTool } =
    useSearch({ from: '/_main/issues' });

  const queryKey = [
    'issueTable',
    intervalInDays,
    culpritCode,
    culpritHarness,
    culpritTool,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchIssueListing(
        intervalInDays,
        culpritCode,
        culpritHarness,
        culpritTool,
      ),
  });
};
