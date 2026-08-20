import type { TreeBranchItem } from './general';
import type { IssueKeys } from './issues';

type PossibleIssueTags = 'mainline' | 'stable' | 'linux-next';

type TIssueVersionData = IssueKeys & {
  trees?: TreeBranchItem[];
  tags?: PossibleIssueTags[];
};

export type IssueKeyList = [string, number][];

export type Incident = {
  first_seen: Date;
  git_commit_hash?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
  git_commit_name?: string;
  tree_name?: string;
  checkout_id?: string;
  issue_version?: string;
};

export type NextCheckout = {
  checkout_id?: string;
  start_time?: Date;
  git_commit_hash?: string;
  git_commit_name?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
  tree_name?: string;
  origin: string;
};

type TExtraIssuesData = {
  first_incident: Incident;
  last_incident: Incident;
  next_checkout?: NextCheckout | null;
  versions: Record<number, TIssueVersionData>;
};

export type IssueExtraDetailsDict = Record<string, TExtraIssuesData>;

export type IssueExtraDetailsResponse = {
  issues: IssueExtraDetailsDict;
};
