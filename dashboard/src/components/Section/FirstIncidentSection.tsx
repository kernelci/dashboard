import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import type { FirstIncident, LastIncident } from '@/types/issueExtras';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import type { ISection, ISubsection, SubsectionLink } from './Section';

const getFirstIncidentInfos = (
  firstIncident: FirstIncident,
): SubsectionLink[] => [
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

const getLastIncidentInfos = (lastIncident: LastIncident): SubsectionLink[] => [
  {
    title: 'global.treeBranchHash',
    linkText: (
      <TreeDetailsLink
        treeName={lastIncident.tree_name}
        gitBranch={lastIncident.git_repository_branch}
        commitHash={lastIncident.git_commit_hash}
        gitUrl={lastIncident.git_repository_url}
        commitName={lastIncident.git_commit_name}
        showFullLabel
      />
    ),
  },
  {
    title: 'issue.lastSeen',
    linkText: (
      <TooltipDateTime
        dateTime={lastIncident.last_seen}
        lineBreak={true}
        showRelative={true}
      />
    ),
  },
];

export const getFirstIncidentSection = ({
  firstIncident,
  lastIncident,
  title,
  lastIncidentTitle,
}: {
  firstIncident?: FirstIncident;
  lastIncident?: LastIncident;
  title: string;
  lastIncidentTitle?: string;
}): ISection | undefined => {
  if (!firstIncident && !lastIncident) {
    return;
  }

  const subsections: ISubsection[] = [];

  if (firstIncident) {
    subsections.push({
      infos: getFirstIncidentInfos(firstIncident),
    });
  }

  if (lastIncident) {
    subsections.push({
      title: lastIncidentTitle,
      infos: getLastIncidentInfos(lastIncident),
    });
  }

  return {
    title: title,
    subsections: subsections,
  };
};
