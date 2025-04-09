import type { JSX } from 'react';

import {
  truncateBigText,
  shouldTruncate,
  valueOrEmpty,
  EMPTY_VALUE,
} from '@/lib/string';

import type { FirstIncident } from '@/types/issueExtras';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { LinkIcon } from '@/components/Icons/Link';

import MemoizedLinkItem from '@/components/DetailsLink';

import type { ISection, SubsectionLink } from './Section';

const FirstIncidentLink = ({
  firstIncident,
}: {
  firstIncident: FirstIncident;
}): JSX.Element => {
  if (firstIncident?.git_commit_hash !== undefined) {
    return (
      <MemoizedLinkItem
        to="/tree/$treeId"
        params={{ treeId: firstIncident.git_commit_hash }}
        state={s => s}
        search={previousSearch => ({
          ...previousSearch,
          treeInfo: {
            gitBranch: firstIncident.git_repository_branch,
            gitUrl: firstIncident.git_repository_url,
            headCommitHash: firstIncident.git_commit_hash,
            CommitName: firstIncident.git_commit_name,
            treeName: firstIncident.tree_name,
          },
        })}
      >
        {truncateBigText(firstIncident.git_commit_hash)}
        <LinkIcon className="text-blue text-xl" />
      </MemoizedLinkItem>
    );
  }

  return <>-</>;
};

export const getFirstIncidentSection = ({
  firstIncident,
  title,
}: {
  firstIncident?: FirstIncident;
  title: string;
}): ISection | undefined => {
  if (!firstIncident) {
    return;
  }

  const firstIncidentInfos: SubsectionLink[] = [
    {
      title: 'global.tree',
      linkText: truncateBigText(firstIncident.tree_name),
    },
    {
      title: 'commonDetails.gitRepositoryBranch',
      linkText: valueOrEmpty(firstIncident.git_repository_branch),
    },
    {
      title: 'commonDetails.gitCommitHash',
      linkComponent: firstIncident.git_commit_hash ? (
        <FirstIncidentLink firstIncident={firstIncident} />
      ) : (
        <span>{EMPTY_VALUE}</span>
      ),
      copyValue: firstIncident.git_commit_hash,
    },
    {
      title: 'commonDetails.gitCommitName',
      linkText: valueOrEmpty(firstIncident.git_commit_name),
    },
    {
      title: 'commonDetails.gitRepositoryUrl',
      linkText: shouldTruncate(
        valueOrEmpty(firstIncident.git_repository_url),
      ) ? (
        <TruncatedValueTooltip
          value={firstIncident.git_repository_url}
          isUrl={true}
        />
      ) : (
        valueOrEmpty(firstIncident.git_repository_url)
      ),
      link: firstIncident.git_repository_url,
    },
    {
      title: 'issue.firstSeen',
      linkText: (
        <TooltipDateTime
          dateTime={firstIncident.first_seen}
          lineBreak={true}
          showRelative={true}
        />
      ),
    },
  ];

  return {
    title: title,
    subsections: [
      {
        infos: firstIncidentInfos,
      },
    ],
  };
};
