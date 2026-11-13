import type { RequiredStatusCount } from './general';

export type LabDailyPoint = {
  day: string;
  pass_count: number;
  fail_count: number;
  inconclusive_count: number;
};

export type LabIssue = {
  id: string;
  version: number;
  comment?: string | null;
  report_url?: string | null;
  incidents_info: Partial<RequiredStatusCount>;
};

export type LabDailySeries = {
  builds: LabDailyPoint[];
  boots: LabDailyPoint[];
  tests: LabDailyPoint[];
};

export type LabDetailsTree = {
  key: string;
  tree_name: string;
  git_branch: string;
  commit_name?: string | null;
  commit_hash?: string | null;
  builds: Partial<RequiredStatusCount>;
  boots: Partial<RequiredStatusCount>;
  tests: Partial<RequiredStatusCount>;
  build_issues: LabIssue[];
  boot_issues: LabIssue[];
  test_issues: LabIssue[];
  daily: LabDailySeries;
};

export type LabNamedCount = {
  name: string;
  count: number;
};

export type LabDistribution = {
  platforms: LabNamedCount[];
  configs: LabNamedCount[];
  compilers: LabNamedCount[];
  architectures: LabNamedCount[];
  build_status: Partial<RequiredStatusCount>;
  boot_status: Partial<RequiredStatusCount>;
  test_status: Partial<RequiredStatusCount>;
};

export type LabFill = {
  checkout_total: number;
  checkouts_built: number;
  checkouts_booted: number;
  checkouts_tested: number;
  builds_total: number;
  builds_with_duration: number;
  runs_total: number;
  runs_with_duration: number;
  runs_with_platform: number;
  runs_with_log_url: number;
  runs_with_log_excerpt: number;
};

export type LabDetailsResponse = {
  lab_name: string;
  trees: LabDetailsTree[];
  distribution: LabDistribution;
  fill: LabFill;
};

export type LabBuildRow = {
  tree_name: string;
  git_branch: string;
  config_name: string;
  architecture: string;
  compiler: string;
  status: string;
  start_time?: string | null;
  duration?: number | null;
};

export type LabBootRow = {
  tree_name: string;
  git_branch: string;
  platform: string;
  config_name: string;
  architecture: string;
  compiler: string;
  status: string;
  start_time?: string | null;
  duration?: number | null;
  log_url?: string | null;
  log_excerpt?: string | null;
};

export type LabTestRow = {
  id: string;
  status: string;
  path?: string | null;
  start_time?: string | null;
  duration?: number | null;
  tree_name: string;
  git_repository_branch: string;
  lab: string;
  config_name?: string | null;
  architecture?: string | null;
  compiler?: string | null;
  platform?: string | null;
  log_url?: string | null;
  log_excerpt?: string | null;
  environment_misc?: Record<string, unknown> | null;
};

export type LabAttentionItem = {
  kind: 'boot' | 'test';
  path?: string | null;
  platform: string;
  tree_name: string;
  git_branch: string;
  commit_name?: string | null;
  commit_hash?: string | null;
  config_name: string;
  architecture: string;
  compiler: string;
  last_failure_date: string;
  passed_labs: string[];
};
