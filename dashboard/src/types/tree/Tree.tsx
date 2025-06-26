import type { RequiredStatusCount } from '@/types/general';

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

type BaseTree = {
  git_commit_hash?: string;
  patchset_hash?: string;
  tree_name?: string;
  git_repository_branch?: string;
  start_time?: string;
  git_repository_url?: string;
  git_commit_name?: string;
  git_commit_tags?: string[];
};

type AllTabCounts = {
  build_status?: RequiredStatusCount;
  test_status?: TableTestStatus;
  boot_status?: TableTestStatus;
};

export type TreeTableBody = BaseTree & AllTabCounts;

export type Tree = BaseTree & Required<AllTabCounts>;

export type TreeLatestResponse = {
  tree_name: string;
  git_repository_branch: string;
  api_url: string;
  git_commit_hash: string;
  git_repository_url: string | null;
  git_commit_name: string | null;
};
