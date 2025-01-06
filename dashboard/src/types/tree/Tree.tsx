import type { BuildStatus } from '@/types/general';

export type TreeFastPathResponse = Array<{
  id: string;
  tree_name: string | null;
  git_repository_branch: string;
  git_repository_url: string;
  git_commit_hash: string;
  git_commit_name: string | null;
  patchset_hash: string | null;
  start_time: string;
}>;

export type TreeTableBody = {
  commitHash: string;
  commitName: string;
  patchsetHash: string;
  buildStatus?: BuildStatus;
  tree_name?: string | null;
  testStatus?: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
  bootStatus?: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
  id: string;
  branch: string;
  date: string;
  url: string;
};

export type Tree = {
  git_commit_hash: string | null;
  patchset_hash: string | null;
  tree_names: string[];
  git_repository_branch: string | null;
  start_time: string | null;
  git_repository_url: string | null;
  git_commit_name: string | null;
  build_status: {
    valid: number;
    invalid: number;
    null: number;
    total: number;
  };
  test_status: {
    fail: number;
    error: number;
    miss: number;
    pass: number;
    done: number;
    skip: number;
    null: number;
    total: number;
  };
  boot_status: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
};

export type TreeLatestResponse = {
  api_url: string;
  git_commit_hash: string;
  git_repository_url: string | null;
  git_commit_name: string | null;
};
