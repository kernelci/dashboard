import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  TTestDetails,
  TestStatusHistory,
  TestStatusHistoryParams,
} from '@/types/tree/TestDetails';

import type { TIssue } from '@/types/issues';
import type { ApiUseQueryOptions } from '@/types/api';

import { RequestData } from './commonRequest';

const fetchTestDetails = async (testId: string): Promise<TTestDetails> => {
  const data = await RequestData.get<TTestDetails>(`/api/test/${testId}`);
  return data;
};

export const useTestDetails = (
  testId: string,
  config: ApiUseQueryOptions<TTestDetails> = {
    enabled: true,
    refetchOnWindowFocus: false,
  },
): UseQueryResult<TTestDetails> => {
  return useQuery({
    queryKey: ['testDetailsData', testId],
    queryFn: () => fetchTestDetails(testId),
    ...config,
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
    refetchOnWindowFocus: false,
  });
};

const fetchTestStatusHistory = async (
  params?: TestStatusHistoryParams,
): Promise<TestStatusHistory> => {
  const data = await RequestData.get<TestStatusHistory>(
    `/api/test/status-history`,
    {
      params,
    },
  );
  return data;
};

export const useTestStatusHistory = (
  params?: TestStatusHistoryParams,
): UseQueryResult<TestStatusHistory> => {
  return useQuery({
    queryKey: ['testStatusHistoryData', params],
    queryFn: () => fetchTestStatusHistory(params),
    enabled: params !== undefined && Object.keys(params).length > 0,
  });
};
