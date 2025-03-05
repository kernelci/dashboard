import type { Status } from '@/types/database';

export type TBuildDetails = {
  timestamp: string;
  id: string;
  architecture?: string;
  checkout_id?: string;
  command?: string;
  comment?: string;
  config_name?: string;
  status: Status;
  start_time?: string;
  duration?: string;
  compiler?: string;
  config_url?: string;
  log_url?: string;
  tree_name?: string;
  git_commit_hash?: string;
  git_commit_name?: string;
  git_repository_branch?: string;
  git_repository_url?: string;
  git_commit_tags?: string[];
  origin?: string;
  log_excerpt?: string;
  misc?: Record<string, unknown>;
  input_files?: Record<string, unknown>;
  output_files?: Record<string, unknown>;
};
