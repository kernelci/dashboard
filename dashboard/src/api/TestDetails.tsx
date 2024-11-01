import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TTestDetails } from '@/types/tree/TestDetails';

import type { TIssue } from '@/types/general';

import http from './api';

const fetchTestDetails = async (testId: string): Promise<TTestDetails> => {
  const res = await http.get<TTestDetails>(`/api/tests/test/${testId}`);
  return res.data;
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
  const res = await http.get<TIssue[]>(`/api/test/${testId}/issues`);
  return res.data;
};

export const useTestIssues = (testId: string): UseQueryResult<TIssue[]> => {
  return useQuery({
    queryKey: ['testIssues', testId],
    queryFn: () => fetchTestIssues(testId),
  });
};
