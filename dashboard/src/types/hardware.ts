import type { ShortStatusCount } from './general';

export type HardwareItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
};

export interface HardwareListingResponse {
  hardware: HardwareItem[];
}

export type HardwareSelectorRevision = {
  git_commit_hash: string;
  git_commit_name?: string | null;
  start_time: string;
};

export type HardwareSelectorBranch = {
  git_repository_url: string;
  git_repository_branch: string;
  revisions: HardwareSelectorRevision[];
};

export type HardwareSelectorTree = {
  tree_name: string;
  branches: HardwareSelectorBranch[];
};

export interface HardwareSelectorsResponse {
  trees: HardwareSelectorTree[];
}

export type HardwareRevisionSelection = {
  treeName: string;
  gitRepositoryUrl: string;
  gitBranch: string;
  gitCommitHash: string;
};

export interface HardwareFiltersResponse {
  checkout_origins: string[];
  build_origins: string[];
  test_origins: string[];
  build_labs: string[];
  test_labs: string[];
}
