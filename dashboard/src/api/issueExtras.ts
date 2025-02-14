import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import type {
  IssueExtraDetailsResponse,
  IssueKeyList,
} from '@/types/issueExtras';

import type { TIssue } from '@/types/issues';

import { RequestData } from './commonRequest';

const fetchIssueExtraDetailsData = async (
  issueKeyList?: IssueKeyList,
): Promise<IssueExtraDetailsResponse> => {
  const body = {
    issues: issueKeyList,
  };

  const data = await RequestData.post<IssueExtraDetailsResponse>(
    `/api/issue/extras/`,
    body,
  );

  return data;
};

export interface ITabsIssues {
  buildIssues?: TIssue[];
  bootIssues?: TIssue[];
  testIssues?: TIssue[];
}

const makeIssueKeyList = ({
  buildIssues,
  bootIssues,
  testIssues,
}: ITabsIssues): IssueKeyList => {
  const result: IssueKeyList = [];

  buildIssues?.forEach(issue => {
    result.push([issue.id, issue.version]);
  });
  bootIssues?.forEach(issue => {
    result.push([issue.id, issue.version]);
  });
  testIssues?.forEach(issue => {
    result.push([issue.id, issue.version]);
  });

  return result;
};

export const useIssueExtraDetails = ({
  buildIssues,
  bootIssues,
  testIssues,
  enabled = true,
}: ITabsIssues & {
  enabled: boolean;
}): UseQueryResult<IssueExtraDetailsResponse> => {
  const issueKeyList = makeIssueKeyList({
    buildIssues,
    bootIssues,
    testIssues,
  });

  const isValidBody = issueKeyList.length !== 0;

  return useQuery({
    queryKey: ['issueExtraData', issueKeyList],
    queryFn: () => fetchIssueExtraDetailsData(issueKeyList),
    enabled: isValidBody && enabled,
  });
};
