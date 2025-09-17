import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import type { FirstIncident } from '@/types/issueExtras';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import type { ISection, SubsectionLink } from './Section';

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
      title: 'global.treeBranchHash',
      linkText: (
        <TreeDetailsLink
          treeName={firstIncident.tree_name}
          gitBranch={firstIncident.git_repository_branch}
          commitHash={firstIncident.git_commit_hash}
          gitUrl={firstIncident.git_repository_url}
          commitName={firstIncident.git_commit_name}
          showFullLabel
        />
      ),
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
    {
      title: 'issueDetails.firstIncidentVersion',
      linkText: firstIncident.issue_version,
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
