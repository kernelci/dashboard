import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { TTestDetails } from '@/types/tree/TestDetails';

import http from './api';

const fetchTestDetails = async (testId: string): Promise<TTestDetails> => {
  const res = await http.get<TTestDetails>(`/api/tests/${testId}`);
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
