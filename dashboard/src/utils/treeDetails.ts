import {
  treeDetailsDirectRouteName,
  type TreeDetailsRouteFrom,
  type TTreeInformation,
} from '@/types/tree/TreeDetails';

import { getStringParam } from './utils';

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
