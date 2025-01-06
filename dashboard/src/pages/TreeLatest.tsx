import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useTreeLatest } from '@/api/tree';

import {
  defaultValidadorValues,
  zTableFilterInfoDefault,
} from '@/types/tree/TreeDetails';

import { DEFAULT_DIFF_FILTER } from '@/types/general';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { Skeleton } from '@/components/Skeleton';

export const TreeLatest = (): JSX.Element | void => {
  const searchParams = useSearch({ from: '/tree/$treeName/$branch/' });
  const navigate = useNavigate();
  const { treeName, branch } = useParams({ from: '/tree/$treeName/$branch/' });
  const { isLoading, data, error } = useTreeLatest(
    treeName,
    branch,
    searchParams.origin,
  );

  if (data) {
    navigate({
      to: '/tree/$treeId',
      params: { treeId: data.git_commit_hash },
      search: {
        ...searchParams,
        currentPageTab: defaultValidadorValues.tab,
        diffFilter: DEFAULT_DIFF_FILTER,
        tableFilter: zTableFilterInfoDefault,
        treeInfo: {
          gitBranch: branch,
          gitUrl: data.git_repository_url || undefined,
          treeName: treeName,
          commitName: data.git_commit_name || undefined,
          headCommitHash: data.git_commit_hash,
        },
      },
    });
  } else if (isLoading) {
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );
  } else {
    return (
      <MemoizedSectionError
        isLoading={isLoading}
        errorMessage={error?.message}
      />
    );
  }
};
