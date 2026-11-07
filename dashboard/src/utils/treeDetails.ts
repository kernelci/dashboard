import { HttpStatusCode, isAxiosError } from 'axios';

import { z } from 'zod';

import { ApiError } from '@/api/commonRequest';

import {
  treeDetailsDirectRouteName,
  type TreeDetailsRouteFrom,
  type TTreeInformation,
} from '@/types/tree/TreeDetails';

import { getStringParam } from './utils';

const treeNotFoundSchema = z.object({
  resource: z.enum(['tree', 'branch', 'commit']),
});

export const getMissingTreeResource = (
  error: unknown,
): z.infer<typeof treeNotFoundSchema>['resource'] | undefined => {
  if (error instanceof ApiError) {
    const result = treeNotFoundSchema.safeParse(error.data);
    return result.success ? result.data.resource : undefined;
  }
  if (
    isAxiosError(error) &&
    error.response?.status === HttpStatusCode.NotFound
  ) {
    const result = treeNotFoundSchema.safeParse(error.response.data);
    return result.success ? result.data.resource : undefined;
  }
  return undefined;
};

type SanitizedTreeInfo = TTreeInformation & {
  hash: string;
};

export const sanitizeTreeinfo = ({
  treeInfo,
  params,
  urlFrom,
  summaryUrl,
}: {
  treeInfo: TTreeInformation;
  params: Record<string, string>; // as params from treeDetailsUrls
  urlFrom: TreeDetailsRouteFrom;
  summaryUrl?: string;
}): SanitizedTreeInfo => {
  if (urlFrom === treeDetailsDirectRouteName) {
    return {
      treeName: getStringParam(params, 'treeName'),
      gitBranch: getStringParam(params, 'branch'),
      hash: getStringParam(params, 'hash'),
      commitName: treeInfo.commitName,
      gitUrl: treeInfo.gitUrl ?? summaryUrl,
      // Copying the hash into headCommitHash is meant for the first entering of the page, when there is no hash selected.
      headCommitHash: treeInfo.headCommitHash || getStringParam(params, 'hash'),
    };
  }

  return {
    treeName: treeInfo.treeName,
    gitBranch: treeInfo.gitBranch,
    hash: getStringParam(params, 'treeId'),
    commitName: treeInfo.commitName,
    gitUrl: treeInfo.gitUrl ?? summaryUrl,
    headCommitHash: treeInfo.headCommitHash,
  };
};
