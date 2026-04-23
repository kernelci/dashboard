import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import { useHardwareDetailsCommitHistory } from '@/api/hardwareDetails';
import type {
  CommitHead,
  HardwareDetailsSummary,
} from '@/types/hardware/hardwareDetails';
import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';
import { makeTreeIdentifierKey } from '@/utils/trees';

interface HardwareCommitNavigationGraphProps {
  trees: HardwareDetailsSummary['common']['trees'];
  hardwareId: string;
}

const HardwareCommitNavigationGraph = ({
  trees,
  hardwareId,
}: HardwareCommitNavigationGraphProps): React.ReactNode => {
  const { diffFilter, treeIndexes, currentPageTab, treeCommits, origin } =
    useSearch({
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

  const commitHeads = useMemo(
    (): CommitHead[] =>
      trees.map(treeItem => ({
        treeName: treeItem.tree_name ?? '',
        repositoryUrl: treeItem.git_repository_url ?? '',
        branch: treeItem.git_repository_branch ?? '',
        commitHash: treeItem.head_git_commit_hash ?? '',
      })),
    [trees],
  );

  const { data: commitHistoryData } = useHardwareDetailsCommitHistory(
    {
      origin,
      hardwareId,
      endTimestampInSeconds,
      startTimestampInSeconds,
      commitHeads,
    },
    { enabled: trees.length > 0 },
  );

  const commitsList = useMemo(() => {
    const treeForIdentifier = treeIdx !== null ? trees[treeIdx] : undefined;
    const key = treeForIdentifier
      ? makeTreeIdentifierKey({
          treeName: treeForIdentifier.tree_name ?? '',
          gitRepositoryBranch: treeForIdentifier.git_repository_branch ?? '',
          gitRepositoryUrl: treeForIdentifier.git_repository_url ?? '',
        })
      : '';
    const entries = commitHistoryData?.commit_history_table?.[key] ?? [];
    return entries.map(c => c.git_commit_hash);
  }, [commitHistoryData?.commit_history_table, treeIdx, trees]);

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
      treeName={tree.tree_name}
      headCommitHash={tree.head_git_commit_hash}
      commitsList={commitsList}
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
