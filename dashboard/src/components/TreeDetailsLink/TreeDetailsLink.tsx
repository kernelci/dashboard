import type { JSX } from 'react';

import { EMPTY_VALUE, truncateBigText, valueOrEmpty } from '@/lib/string';

import { LinkIcon } from '@/components/Icons/Link';
import MemoizedLinkItem from '@/components/DetailsLink';

export const TreeDetailsLink = ({
  treeName,
  gitBranch,
  commitHash,
  gitUrl,
  commitName,
  showFullLabel = false,
}: {
  treeName?: string;
  gitBranch?: string;
  commitHash?: string;
  gitUrl?: string;
  commitName?: string;
  showFullLabel?: boolean;
}): JSX.Element => {
  const linkText = showFullLabel
    ? `${valueOrEmpty(treeName)} / ${valueOrEmpty(gitBranch)} / ${truncateBigText(commitHash)}`
    : `${truncateBigText(commitHash)}`;
  const linkIcon = <LinkIcon className="text-blue text-xl" />;

  if (!commitHash) {
    if (!treeName && !gitBranch) {
      return <>{EMPTY_VALUE}</>;
    }
    return <>{linkText}</>;
  }

  if (treeName && gitBranch && commitHash) {
    return (
      <MemoizedLinkItem
        to="/tree/$treeName/$branch/$hash"
        params={{ treeName, branch: gitBranch, hash: commitHash }}
        state={s => s}
        search={s => ({
          origin: s.origin,
        })}
      >
        {linkText}
        {linkIcon}
      </MemoizedLinkItem>
    );
  }

  return (
    <MemoizedLinkItem
      to="/tree/$treeId"
      params={{ treeId: commitHash }}
      state={s => s}
      search={s => ({
        origin: s.origin,
        treeInfo: {
          treeName: treeName,
          gitBranch: gitBranch,
          headCommitHash: commitHash,
          gitUrl: gitUrl,
          commitName: commitName,
        },
      })}
    >
      {linkText}
      {linkIcon}
    </MemoizedLinkItem>
  );
};
