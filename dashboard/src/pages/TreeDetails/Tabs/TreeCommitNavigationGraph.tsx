import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';
import type {
  TTreeInformation,
  TreeDetailsRouteFrom,
} from '@/types/tree/TreeDetails';

import { treeDetailsFromMap } from '@/types/tree/TreeDetails';
import { getStringParam } from '@/utils/treeDetails';

const TreeCommitNavigationGraph = ({
  urlFrom,
  treeUrl,
}: {
  urlFrom: TreeDetailsRouteFrom;
  treeUrl?: string;
}): React.ReactNode => {
  const { origin, currentPageTab, diffFilter, treeInfo } = useSearch({
    from: urlFrom,
  });

  const params = useParams({
    from: urlFrom,
  });

  const sanitizedTreeInfo = useMemo((): TTreeInformation & {
    hash: string;
  } => {
    return {
      treeName: treeInfo.treeName || getStringParam(params, 'treeName'),
      gitBranch: treeInfo.gitBranch || getStringParam(params, 'branch'),
      headCommitHash: treeInfo.headCommitHash || getStringParam(params, 'hash'),
      gitUrl: treeInfo.gitUrl || treeUrl,
      hash: getStringParam(params, 'treeId') || getStringParam(params, 'hash'),
    };
  }, [params, treeInfo, treeUrl]);

  const navigate = useNavigate({
    from: treeDetailsFromMap[urlFrom],
  });

  const markClickHandle = useCallback(
    (commitHash: string, commitName?: string) => {
      navigate({
        to: '/tree/$treeId',
        params: {
          treeId: commitHash,
        },
        state: s => ({
          ...s,
          id: commitHash,
        }),
        search: previousParams => ({
          ...previousParams,
          treeInfo: {
            ...previousParams.treeInfo,
            commitName: commitName,
            commitHash: commitHash,
          },
        }),
      });
    },
    [navigate],
  );

  return (
    <CommitNavigationGraph
      origin={origin}
      gitBranch={sanitizedTreeInfo.gitBranch}
      gitUrl={sanitizedTreeInfo.gitUrl}
      treeId={sanitizedTreeInfo.hash}
      headCommitHash={sanitizedTreeInfo.headCommitHash}
      onMarkClick={markClickHandle}
      diffFilter={diffFilter}
      currentPageTab={currentPageTab}
    />
  );
};

export default TreeCommitNavigationGraph;
