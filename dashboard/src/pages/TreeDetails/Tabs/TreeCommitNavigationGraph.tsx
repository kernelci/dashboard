import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';

const TreeCommitNavigationGraph = (): React.ReactNode => {
  const {
    origin,
    currentPageTab,
    diffFilter,
    treeInfo: { gitUrl, gitBranch, headCommitHash },
  } = useSearch({ from: '/tree/$treeId' });

  const { treeId } = useParams({
    from: '/tree/$treeId',
  });

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const markClickHandle = useCallback(
    (commitHash: string, commitName?: string) => {
      navigate({
        to: '/tree/$treeId',
        params: {
          treeId: commitHash,
        },
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
      gitBranch={gitBranch}
      gitUrl={gitUrl}
      treeId={treeId}
      headCommitHash={headCommitHash}
      onMarkClick={markClickHandle}
      diffFilter={diffFilter}
      currentPageTab={currentPageTab}
    />
  );
};

export default TreeCommitNavigationGraph;
