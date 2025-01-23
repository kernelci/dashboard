import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TErrorWithStatus, TIssueDetails } from '@/types/issueDetails';

import type { BuildsTableBuild, TestHistory } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchIssueDetailsData = async (
  issueId: string,
  versionNumber: string,
): Promise<TIssueDetails> => {
  const res = await RequestData.get<TIssueDetails & { _timestamp: string }>(
    `/api/issue/${issueId}/version/${versionNumber}`,
  );

  const { _timestamp, ...data } = res;
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
  const data = await RequestData.get<TestHistory[]>(
    `/api/issue/${issueId}/version/${versionNumber}/tests`,
  );

  return data;
};

export const useIssueDetailsTests = (
  issueId: string,
  versionNumber: string,
): UseQueryResult<TestHistory[], TErrorWithStatus> => {
  return useQuery({
    queryKey: ['issueTestsData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsTests(issueId, versionNumber),
  });
};

const fetchIssueDetailsBuilds = async (
  issueId: string,
  versionNumber: string,
): Promise<BuildsTableBuild[]> => {
  const data = await RequestData.get<BuildsTableBuild[]>(
    `/api/issue/${issueId}/version/${versionNumber}/builds`,
  );

  return data;
};

export const useIssueDetailsBuilds = (
  issueId: string,
  versionNumber: string,
): UseQueryResult<BuildsTableBuild[], TErrorWithStatus> => {
  return useQuery({
    queryKey: ['issueBuildsData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsBuilds(issueId, versionNumber),
  });
};
