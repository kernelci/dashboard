import { shouldTruncate, valueOrEmpty } from '@/lib/string';

import type { Incident } from '@/types/issueExtras';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import type { ISection, ISubsection, SubsectionLink } from './Section';

const getIncidentInfos = (firstIncident: Incident): SubsectionLink[] => [
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
    linkText: shouldTruncate(valueOrEmpty(firstIncident.git_repository_url)) ? (
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
    title: 'issue.seen',
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

export const getIncidentsSection = ({
  firstIncident,
  lastIncident,
  title,
  lastIncidentTitle,
}: {
  firstIncident?: Incident;
  lastIncident?: Incident;
  title: string;
  lastIncidentTitle?: string;
}): ISection | undefined => {
  if (!firstIncident && !lastIncident) {
    return;
  }

  const subsections: ISubsection[] = [];

  if (firstIncident) {
    subsections.push({
      infos: getIncidentInfos(firstIncident),
    });
  }

  if (lastIncident) {
    subsections.push({
      title: lastIncidentTitle,
      infos: getIncidentInfos(lastIncident),
    });
  }

  return {
    title: title,
    subsections: subsections,
  };
};
