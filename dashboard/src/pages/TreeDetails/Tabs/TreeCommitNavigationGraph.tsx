import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import { useCommits } from '@/api/commitHistory';
import CommitNavigationGraph from '@/components/CommitNavigationGraph/CommitNavigationGraph';
import {
  treeDetailsDirectRouteName,
  treeDetailsFromMap,
  type TTreeInformation,
  type TreeDetailsRouteFrom,
} from '@/types/tree/TreeDetails';
import { sanitizeTreeinfo } from '@/utils/treeDetails';

const TreeCommitNavigationGraph = ({
  urlFrom,
  treeName,
  summaryTreeUrl,
}: {
  urlFrom: TreeDetailsRouteFrom;
  treeName?: string;
  summaryTreeUrl?: string;
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
    return sanitizeTreeinfo({
      treeInfo,
      params,
      urlFrom,
      summaryUrl: summaryTreeUrl,
    });
  }, [params, summaryTreeUrl, treeInfo, urlFrom]);

  const { data: commitsData } = useCommits({
    origin,
    gitUrl: sanitizedTreeInfo.gitUrl ?? '',
    gitBranch: sanitizedTreeInfo.gitBranch ?? '',
    treeName,
  });

  const commitsList = useMemo(
    () => commitsData?.map(c => c.git_commit_hash) ?? [],
    [commitsData],
  );

  const navigate = useNavigate({
    from: treeDetailsFromMap[urlFrom],
  });

  const markClickHandle = useCallback(
    (commitHash: string, commitName?: string) => {
      if (urlFrom === treeDetailsDirectRouteName) {
        navigate({
          to: treeDetailsFromMap[urlFrom],
          params: {
            treeName: sanitizedTreeInfo.treeName!,
            branch: sanitizedTreeInfo.gitBranch!,
            hash: commitHash,
          },
          state: s => ({
            ...s,
            id: commitHash,
          }),
          search: previousParams => ({
            ...previousParams,
            treeInfo: {
              ...previousParams.treeInfo,
              headCommitHash: sanitizedTreeInfo.headCommitHash,
            },
          }),
        });
      } else {
        navigate({
          to: treeDetailsFromMap[urlFrom],
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
      }
    },
    [
      navigate,
      sanitizedTreeInfo.gitBranch,
      sanitizedTreeInfo.headCommitHash,
      sanitizedTreeInfo.treeName,
      urlFrom,
    ],
  );

  return (
    <CommitNavigationGraph
      origin={origin}
      gitBranch={sanitizedTreeInfo.gitBranch}
      gitUrl={sanitizedTreeInfo.gitUrl}
      treeId={sanitizedTreeInfo.hash}
      headCommitHash={sanitizedTreeInfo.headCommitHash}
      commitsList={commitsList}
      onMarkClick={markClickHandle}
      diffFilter={diffFilter}
      currentPageTab={currentPageTab}
      treeName={treeName}
      treeUrlFrom={urlFrom}
    />
  );
};

export default TreeCommitNavigationGraph;
