import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TIssueDetails } from '@/types/issueDetails';

import type { TestHistory } from '@/types/general';

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

const fetchIssueDetailsTests = async (
  issueId: string,
  versionNumber: string,
): Promise<TestHistory[]> => {
  const res = await http.get(
    `/api/issue/${issueId}/version/${versionNumber}/tests`,
  );

  return res.data;
};

export const useIssueDetailsTests = (
  issueId: string,
  versionNumber: string,
): UseQueryResult<TestHistory[]> => {
  return useQuery({
    queryKey: ['issueTestsData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsTests(issueId, versionNumber),
  });
};
