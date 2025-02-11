type IncidentsInfo = { incidentsCount: number };

export type IssueKeys = {
  id: string;
  version: number;
};

export type TIssue = IssueKeys & {
  comment?: string;
  report_url?: string;
  incidents_info: IncidentsInfo;
};
