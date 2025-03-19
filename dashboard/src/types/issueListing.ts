import type { FirstIncident } from './issueExtras';
import type { IssueKeys } from './issues';

export type IssueListingItem = IssueKeys & {
  field_timestamp: Date;
  comment?: string;
  culprit_code?: boolean;
  origin: string;
  culprit_tool?: boolean;
  culprit_harness?: boolean;
};

export type IssueListingResponse = {
  issues: IssueListingItem[];
  extras: Record<string, FirstIncident>;
};

export type IssueListingTableItem = IssueListingItem & FirstIncident;
