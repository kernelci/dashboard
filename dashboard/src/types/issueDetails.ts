export type TIssueDetails = {
  timestamp: string;
  id: string;
  version: number;
  origin: string;
  report_url?: string;
  report_subject?: string;
  culprit_code?: boolean;
  culprit_tool?: boolean;
  culprit_harness?: boolean;
  build_valid?: boolean;
  test_status?: string;
  comment?: string;
  misc?: Record<string, unknown>;
};
