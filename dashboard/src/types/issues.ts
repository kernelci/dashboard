import type { RequiredStatusCount } from './general';

export type IssueKeys = {
  id: string;
  version: number;
};

export type TIssue = IssueKeys & {
  comment?: string;
  report_url?: string;
  incidents_info: RequiredStatusCount;
};
