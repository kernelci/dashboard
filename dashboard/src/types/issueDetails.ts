import type { IssueExtraDetailsDict } from './issueExtras';
import type { IssueKeys } from './issues';

export type TIssueDetails = IssueKeys & {
  timestamp: string;
  origin: string;
  report_url?: string;
  report_subject?: string;
  culprit_code?: boolean;
  culprit_tool?: boolean;
  culprit_harness?: boolean;
  comment?: string;
  misc?: Record<string, unknown>;
  categories?: string[];
  extra?: IssueExtraDetailsDict;
};
