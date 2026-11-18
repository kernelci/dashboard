import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { useTreeLatest } from '@/api/tree';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { TreeQueryError } from '@/pages/TreeDetails/TreeQueryError';

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
  const { origin } = useSearch({ from: urlFrom });
  const navigate = useNavigate();
  const params = useParams({
    from: urlFrom,
  });

  const { treeName, branch } = params;
  const hash = 'hash' in params ? params.hash : undefined;

  const { data, status, error } = useTreeLatest(treeName, branch, origin, hash);

  if (data) {
    navigate({
      to: '/tree/$treeName/$branch/$hash',
      params: {
        treeName: data.tree_name,
        branch: data.git_repository_branch,
        hash: data.git_commit_hash,
      },
      search: s => ({
        ...s,
        origin: origin,
      }),
    });
  }

  return (
    <QuerySwitcher
      data={data}
      status={status}
      customError={
        <TreeQueryError
          error={error}
          treeName={treeName}
          branch={branch}
          hash={hash}
          origin={origin}
        />
      }
    >
      <FormattedMessage id="global.redirecting" />
    </QuerySwitcher>
  );
};
