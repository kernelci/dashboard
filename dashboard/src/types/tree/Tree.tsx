import type { ShortStatusCount } from '@/types/general';

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

export type TreeListingItem = BaseTree & {
  build_status: ShortStatusCount;
  test_status: ShortStatusCount;
  boot_status: ShortStatusCount;
};

export type TreeLatestResponse = {
  tree_name: string;
  git_repository_branch: string;
  api_url: string;
  git_commit_hash: string;
  git_repository_url: string | null;
  git_commit_name: string | null;
};
