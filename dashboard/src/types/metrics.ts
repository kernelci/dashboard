export type BuildIncidentsCount = {
  total_incidents: number;
  n_new_issues: number;
  n_existing_issues: number;
  n_total_issues: number;
};

export type TopIssue = {
  id: string;
  version: number;
  comment: string;
  total_incidents: number;
};

export type LabMetricsData = {
  builds: number;
  boots: number;
  tests: number;
};

export type MetricsResponse = {
  n_trees: number;
  n_checkouts: number;
  n_builds: number;
  n_tests: number;
  n_issues: number;
  n_incidents: number;
  build_incidents_by_origin: Record<string, BuildIncidentsCount>;
  top_issues_by_origin: Record<string, TopIssue[]>;
  new_issues_by_origin: Record<string, TopIssue[]>;
  lab_maps: Record<string, LabMetricsData>;
  prev_n_trees: number;
  prev_n_checkouts: number;
  prev_n_builds: number;
  prev_n_tests: number;
  prev_lab_maps: Record<string, LabMetricsData>;
};
