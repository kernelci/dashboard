import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';

interface ICommitNavigationGraph {
  trees: THardwareDetails['trees'];
  hardwareId: string;
}
const HardwareCommitNavigationGraph = ({
  trees,
  hardwareId,
}: ICommitNavigationGraph): React.ReactNode => {
  const { diffFilter, treeIndexes, origin, currentPageTab, treeCommits } =
    useSearch({
      from: '/hardware/$hardwareId',
    });

  const navigate = useNavigate({ from: '/hardware/$hardwareId/' });

  const diffFilterWithHardware = useMemo(
    () => ({ ...diffFilter, hardware: { [hardwareId]: true } }),
    [diffFilter, hardwareId],
  );

  const treeIdx =
    trees.length === 1 ? 0 : treeIndexes?.length === 1 ? treeIndexes[0] : null;
  const tree = treeIdx !== null && trees[treeIdx];

  const markClickHandle = useCallback(
    (commitHash: string) => {
      if (treeIdx === null) return;

      navigate({
        search: current => ({
          ...current,
          treeCommits: { ...current.treeCommits, [treeIdx]: commitHash },
        }),
      });
    },
    [navigate, treeIdx],
  );

  if (!tree) return <></>;

  const treeId = treeCommits?.[treeIdx] ?? tree['headGitCommitHash'];

  return (
    <CommitNavigationGraph
      origin={origin}
      gitBranch={tree.gitRepositoryBranch}
      gitUrl={tree.gitRepositoryUrl}
      treeId={treeId}
      headCommitHash={tree.headGitCommitHash}
      onMarkClick={markClickHandle}
      diffFilter={diffFilterWithHardware}
      currentPageTab={currentPageTab}
    />
  );
};

export default HardwareCommitNavigationGraph;
