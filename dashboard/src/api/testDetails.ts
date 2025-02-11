import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TTestDetails } from '@/types/tree/TestDetails';

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

export const useTestIssues = (testId: string): UseQueryResult<TIssue[]> => {
  return useQuery({
    queryKey: ['testIssues', testId],
    enabled: testId !== '',
    queryFn: () => fetchTestIssues(testId),
  });
};
