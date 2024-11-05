import { memo } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useTreeCommitHistory } from '@/api/TreeDetails';
import { mapFilterToReq } from '@/pages/TreeDetails/TreeDetailsFilter';
import CommitNavigationChart from '@/pages/Charts/CommitNavigationChart';

const CommitNavigationTreeDetailsGraph = (): JSX.Element => {
  const {
    origin,
    currentTreeDetailsTab,
    diffFilter,
    treeInfo: { gitUrl, gitBranch, headCommitHash },
  } = useSearch({ from: '/tree/$treeId/' });

  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const reqFilter = mapFilterToReq(diffFilter);

  const { data, status } = useTreeCommitHistory(
    {
      gitBranch: gitBranch ?? '',
      gitUrl: gitUrl ?? '',
      commitHash: headCommitHash ?? '',
      origin: origin,
      filter: reqFilter,
    },
    {
      enabled: !!gitBranch && !!gitUrl,
    },
  );

  const navigateToCommit = (commitHash: string, commitName: string): void => {
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
  };

  return (
    <CommitNavigationChart
      data={data}
      currentDetailsTab={currentTreeDetailsTab.split('.').pop() ?? ''}
      currentCommitHash={treeId}
      commitNavigate={navigateToCommit}
      status={status}
    />
  );
};

export default memo(CommitNavigationTreeDetailsGraph);
