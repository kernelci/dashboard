import type { FirstIncident } from './issueExtras';
import type { IssueKeys } from './issues';

export type IssueListingItem = IssueKeys & {
  field_timestamp: Date;
  comment?: string;
  culprit_code?: boolean;
  origin: string;
  culprit_tool?: boolean;
  culprit_harness?: boolean;
  categories?: string[];
};

export type IssueListingFilters = {
  categories: string[];
  origins: string[];
  culprits: string[];
};

export type IssueListingResponse = {
  issues: IssueListingItem[];
  extras: Record<string, FirstIncident>;
  filters: IssueListingFilters;
};

export type IssueListingTableItem = IssueListingItem & FirstIncident;
