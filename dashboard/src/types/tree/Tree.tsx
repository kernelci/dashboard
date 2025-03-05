import type { BuildStatus } from '@/types/general';

export type TreeFastPathResponse = Array<{
  id: string;
  tree_name?: string;
  git_repository_branch: string;
  git_repository_url: string;
  git_commit_hash: string;
  git_commit_name?: string;
  git_commit_tags?: string[];
  patchset_hash?: string;
  start_time: string;
}>;

export type TableTestStatus = {
  done: number;
  pass: number;
  error: number;
  fail: number;
  skip: number;
  miss: number;
  null: number;
};

export type TreeTableBody = {
  commitHash: string;
  commitName: string;
  commitTag?: string[];
  patchsetHash: string;
  buildStatus?: BuildStatus;
  tree_name?: string | null;
  testStatus?: TableTestStatus;
  bootStatus?: TableTestStatus;
  id: string;
  branch: string;
  date: string;
  url: string;
};

export type Tree = {
  git_commit_hash?: string;
  patchset_hash?: string;
  tree_names: string[];
  git_repository_branch?: string;
  start_time?: string;
  git_repository_url?: string;
  git_commit_name?: string;
  git_commit_tags: string[];
  build_status: BuildStatus;
  test_status: TableTestStatus;
  boot_status: TableTestStatus;
};

export type TreeLatestResponse = {
  api_url: string;
  git_commit_hash: string;
  git_repository_url: string | null;
  git_commit_name: string | null;
};
