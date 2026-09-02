import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import type { NextCheckout } from '@/types/issueExtras';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import type { ISection, SubsectionLink } from './Section';

const getNextCheckoutInfos = (nextCheckout: NextCheckout): SubsectionLink[] => [
  {
    title: 'global.treeBranchHash',
    linkText: (
      <TreeDetailsLink
        treeName={nextCheckout.tree_name}
        gitBranch={nextCheckout.git_repository_branch}
        commitHash={nextCheckout.git_commit_hash}
        gitUrl={nextCheckout.git_repository_url}
        commitName={nextCheckout.git_commit_name}
        showFullLabel
      />
    ),
  },
  {
    title: 'commonDetails.gitCommitName',
    linkText: valueOrEmpty(nextCheckout.git_commit_name),
  },
  {
    title: 'commonDetails.gitRepositoryUrl',
    linkText: shouldTruncate(valueOrEmpty(nextCheckout.git_repository_url)) ? (
      <TruncatedValueTooltip
        value={nextCheckout.git_repository_url}
        isUrl={true}
      />
    ) : (
      valueOrEmpty(nextCheckout.git_repository_url)
    ),
    link: nextCheckout.git_repository_url,
  },
  {
    title: 'global.startTime',
    linkText: (
      <TooltipDateTime
        dateTime={nextCheckout.start_time ?? ''}
        lineBreak={true}
        showRelative={true}
      />
    ),
  },
  {
    title: 'global.origin',
    linkText: valueOrEmpty(nextCheckout.origin),
  },
];

export const getNextCheckoutSection = ({
  nextCheckout,
  title,
}: {
  nextCheckout?: NextCheckout | null;
  title: string;
}): ISection | undefined => {
  if (!nextCheckout) {
    return;
  }

  return {
    title: title,
    subsections: [
      {
        infos: getNextCheckoutInfos(nextCheckout),
      },
    ],
  };
};
