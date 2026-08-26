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

export type Checkout = {
  start_time: Date;
  git_commit_hash?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
  git_commit_name?: string;
  tree_name?: string;
  checkout_id?: string;
};

export type TreeSeenData = {
  first_incident: Incident;
  last_incident: Incident;
  first_good_checkout?: Checkout;
};

type TExtraIssuesData = {
  first_incident: Incident;
  last_incident: Incident;
  per_tree?: TreeSeenData[];
  versions: Record<number, TIssueVersionData>;
};

export type IssueExtraDetailsDict = Record<string, TExtraIssuesData>;

export type IssueExtraDetailsResponse = {
  issues: IssueExtraDetailsDict;
};
