import type { TreeBranchItem } from './general';
import type { IssueKeys } from './issues';

type PossibleIssueTags = 'mainline' | 'stable' | 'linux-next';

type TIssueExtraDetails = IssueKeys & {
  first_seen?: Date;
  trees?: TreeBranchItem[];
  tags?: PossibleIssueTags[];
};

export type IssueKeyList = [string, number][];

export type IssueExtraDetailsDict = Record<
  string,
  Record<number, TIssueExtraDetails>
>;

export type IssueExtraDetailsResponse = {
  issues: IssueExtraDetailsDict;
};
