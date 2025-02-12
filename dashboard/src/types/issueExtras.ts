import type { TreeBranchItem } from './general';
import type { IssueKeys } from './issues';

type PossibleIssueTags = 'mainline' | 'stable' | 'linux-next';

type TIssueVersionData = IssueKeys & {
  trees?: TreeBranchItem[];
  tags?: PossibleIssueTags[];
};

export type IssueKeyList = [string, number][];

type FirstIncident = {
  first_seen: Date;
  git_commit_hash?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
};

type TExtraIssuesData = {
  first_incident: FirstIncident;
  versions: Record<number, TIssueVersionData>;
};

export type IssueExtraDetailsDict = Record<string, TExtraIssuesData>;

export type IssueExtraDetailsResponse = {
  issues: IssueExtraDetailsDict;
};
