import type { Status } from '@/types/database';

export type TTestDetails = {
  architecture: string;
  build_id: string;
  compiler: string;
  config_name: string;
  git_commit_hash: string;
  git_repository_branch: string;
  git_repository_url: string;
  git_commit_tags?: string[];
  id: string;
  log_excerpt: string | undefined;
  log_url: string | undefined;
  path: string;
  start_time: string;
  status: Status;
  environment_compatible?: string[];
  environment_misc?: Record<string, unknown>;
  misc?: Record<string, unknown>;
  input_files?: Record<string, unknown>;
  output_files?: Record<string, unknown>;
  tree_name?: string;
  origin?: string;
  field_timestamp: string;
};

export type TestStatusHistoryItem = {
  start_time: string;
  id: string;
  status: Status;
  git_commit_hash?: string;
};

type PossibleRegressionType =
  | 'regression'
  | 'fixed'
  | 'unstable'
  | 'pass'
  | 'fail';

export type TestStatusHistory = {
  status_history: TestStatusHistoryItem[];
  regression_type: PossibleRegressionType;
};

export type TestStatusHistoryParams = {
  path?: string;
  origin?: string;
  git_repository_url?: string;
  git_repository_branch?: string;
  platform?: string;
  current_test_start_time?: string;
  config_name?: string;
  field_timestamp?: string;
};
