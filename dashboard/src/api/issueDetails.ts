import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TIssueDetails } from '@/types/issueDetails';

import http from './api';

const fetchIssueDetailsData = async (
  issueId: string,
  versionNumber: string,
): Promise<TIssueDetails> => {
  const res = await http.get(`/api/issue/${issueId}/version/${versionNumber}`);

  const { _timestamp, ...data } = res.data;
  data.timestamp = _timestamp;
  return data;
};

export const useIssueDetails = (
  issueId: string,
  versionNumber: string,
): UseQueryResult<TIssueDetails> => {
  return useQuery({
    queryKey: ['issueData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsData(issueId, versionNumber),
  });
};
