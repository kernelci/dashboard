import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import type { HardwareDetailsSummary } from '@/types/hardware/hardwareDetails';
import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';

interface ICommitNavigationGraph {
  trees: HardwareDetailsSummary['common']['trees'];
  hardwareId: string;
}
const HardwareCommitNavigationGraph = ({
  trees,
  hardwareId,
}: ICommitNavigationGraph): React.ReactNode => {
  const { diffFilter, treeIndexes, currentPageTab, treeCommits } = useSearch({
    from: '/_main/hardware/$hardwareId',
  });
  const { startTimestampInSeconds, endTimestampInSeconds } = useSearch({
    from: '/_main/hardware/$hardwareId/',
  });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const diffFilterWithHardware = useMemo(
    () => ({ ...diffFilter, hardware: { [hardwareId]: true } }),
    [diffFilter, hardwareId],
  );

  const treeIdx =
    trees.length === 1 ? 0 : treeIndexes?.length === 1 ? treeIndexes[0] : null;
  const tree = treeIdx !== null && trees[treeIdx];

  const markClickHandle = useCallback(
    (commitHash: string) => {
      if (treeIdx === null) {
        return;
      }

      navigate({
        search: current => ({
          ...current,
          treeCommits: { ...treeCommits, [treeIdx]: commitHash },
        }),
        state: s => s,
      });
    },
    [navigate, treeIdx, treeCommits],
  );

  if (!tree) {
    return <></>;
  }

  const treeId = treeCommits?.[treeIdx] ?? tree['head_git_commit_hash'];

  return (
    <CommitNavigationGraph
      origin={tree.origin}
      gitBranch={tree.git_repository_branch}
      gitUrl={tree.git_repository_url}
      treeId={treeId}
      headCommitHash={tree.head_git_commit_hash}
      onMarkClick={markClickHandle}
      diffFilter={diffFilterWithHardware}
      currentPageTab={currentPageTab}
      endTimestampInSeconds={endTimestampInSeconds}
      startTimestampInSeconds={startTimestampInSeconds}
      buildsRelatedToFilteredTestsOnly={true}
    />
  );
};

export default HardwareCommitNavigationGraph;
