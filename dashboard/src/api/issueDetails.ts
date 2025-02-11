import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TIssueDetails } from '@/types/issueDetails';

import type {
  BuildsTableBuild,
  TErrorWithStatus,
  TestHistory,
} from '@/types/general';

import { RequestData } from './commonRequest';

const fetchIssueDetailsData = async (
  issueId: string,
  versionNumber?: number,
): Promise<TIssueDetails> => {
  const params = {
    version: versionNumber,
  };

  const res = await RequestData.get<TIssueDetails & { _timestamp: string }>(
    `/api/issue/${issueId}`,
    { params },
  );

  const { _timestamp, ...data } = res;
  data.timestamp = _timestamp;
  return data;
};

export const useIssueDetails = (
  issueId: string,
  versionNumber?: number,
): UseQueryResult<TIssueDetails> => {
  return useQuery({
    queryKey: ['issueData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsData(issueId, versionNumber),
  });
};

const fetchIssueDetailsTests = async (
  issueId: string,
  versionNumber?: number,
): Promise<TestHistory[]> => {
  const params = {
    version: versionNumber,
  };

  const data = await RequestData.get<TestHistory[]>(
    `/api/issue/${issueId}/tests`,
    { params },
  );

  return data;
};

export const useIssueDetailsTests = (
  issueId: string,
  versionNumber?: number,
): UseQueryResult<TestHistory[], TErrorWithStatus> => {
  return useQuery({
    queryKey: ['issueTestsData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsTests(issueId, versionNumber),
    retry: 1,
  });
};

const fetchIssueDetailsBuilds = async (
  issueId: string,
  versionNumber?: number,
): Promise<BuildsTableBuild[]> => {
  const params = {
    version: versionNumber,
  };

  const data = await RequestData.get<BuildsTableBuild[]>(
    `/api/issue/${issueId}/builds`,
    { params },
  );

  return data;
};

export const useIssueDetailsBuilds = (
  issueId: string,
  versionNumber?: number,
): UseQueryResult<BuildsTableBuild[], TErrorWithStatus> => {
  return useQuery({
    queryKey: ['issueBuildsData', issueId, versionNumber],
    queryFn: () => fetchIssueDetailsBuilds(issueId, versionNumber),
    retry: 1,
  });
};
