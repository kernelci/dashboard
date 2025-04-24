import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { useTreeLatest } from '@/api/tree';

import {
  defaultValidadorValues,
  zTableFilterInfoDefault,
} from '@/types/tree/TreeDetails';

import { DEFAULT_DIFF_FILTER } from '@/types/general';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

type TreeLatestFrom =
  | '/_main/(alternatives)/c/$treeName/$branch/'
  | '/_main/tree/$treeName/$branch/'
  | '/_main/checkout/$treeName/$branch/';

type TreeLatestWithHashFrom =
  | '/_main/(alternatives)/c/$treeName/$branch/$hash/'
  | '/_main/tree/$treeName/$branch/$hash/'
  | '/_main/checkout/$treeName/$branch/$hash/';

export const TreeLatest = ({
  urlFrom,
}: {
  urlFrom: TreeLatestFrom | TreeLatestWithHashFrom;
}): JSX.Element => {
  const searchParams = useSearch({ from: urlFrom });
  const navigate = useNavigate();
  const params = useParams({
    from: urlFrom,
  });

  const { treeName, branch } = params;
  const hash = 'hash' in params ? params.hash : undefined;

  const { isLoading, data, status, error } = useTreeLatest(
    treeName,
    branch,
    searchParams.origin,
    hash,
  );

  if (data) {
    navigate({
      to: '/tree/$treeId',
      params: { treeId: data.git_commit_hash },
      search: s => ({
        ...s,
        origin: searchParams.origin,
        currentPageTab: defaultValidadorValues.tab,
        diffFilter: DEFAULT_DIFF_FILTER,
        tableFilter: zTableFilterInfoDefault,
        treeInfo: {
          gitBranch: branch,
          gitUrl: data.git_repository_url || undefined,
          treeName: data.tree_name,
          commitName: data.git_commit_name || undefined,
          headCommitHash: data.git_commit_hash,
        },
      }),
    });
  }

  return (
    <QuerySwitcher
      data={data}
      status={status}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          emptyLabel="treeDetails.notFound"
        />
      }
    >
      <FormattedMessage id="global.redirecting" />
    </QuerySwitcher>
  );
};
