import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  TTestDetails,
  TTestStatusHistory,
} from '@/types/tree/TestDetails';

import type { TIssue } from '@/types/issues';

import { RequestData } from './commonRequest';

const fetchTestDetails = async (testId: string): Promise<TTestDetails> => {
  const data = await RequestData.get<TTestDetails>(`/api/test/${testId}`);
  return data;
};

export const useTestDetails = (
  testId: string,
): UseQueryResult<TTestDetails> => {
  return useQuery({
    queryKey: ['testDetailsData', testId],
    queryFn: () => fetchTestDetails(testId),
  });
};

const fetchTestIssues = async (testId: string): Promise<TIssue[]> => {
  const data = await RequestData.get<TIssue[]>(`/api/test/${testId}/issues`);

  return data;
};

export const useTestIssues = (
  testId: string,
  enabled = true,
): UseQueryResult<TIssue[]> => {
  return useQuery({
    queryKey: ['testIssues', testId],
    enabled: testId !== '' && enabled,
    queryFn: () => fetchTestIssues(testId),
  });
};

const fetchTestStatusHistory = async (
  params?: Record<string, unknown>,
): Promise<TTestStatusHistory> => {
  const data = await RequestData.get<TTestStatusHistory>(
    `/api/test/status-history`,
    {
      params,
    },
  );
  return data;
};

export const useTestStatusHistory = (params?: {
  path?: string;
  origin?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
  platform?: string;
  current_test_timestamp?: string;
}): UseQueryResult<TTestStatusHistory> => {
  return useQuery({
    queryKey: ['testDetailsData', params],
    queryFn: () => fetchTestStatusHistory(params),
    enabled: params !== undefined && Object.keys(params).length > 0,
  });
};
