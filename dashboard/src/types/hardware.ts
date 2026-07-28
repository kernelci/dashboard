import type { ShortStatusCount } from './general';

export type HardwareItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
};

export type HardwareListingApiItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
};

export interface HardwareListingResponse {
  hardware: HardwareListingApiItem[];
}

/** The five filters of the hardware listing, as they appear in the URL. */
export type HardwareListingFilters = {
  checkoutOrigin: string;
  buildOrigin: string;
  testOrigin: string;
  buildLab: string;
  testLab: string;
};

/** Values available for each filter, none of them narrowed by the others. */
export type HardwareFiltersResponse = {
  checkout_origins: string[];
  build_origins: string[];
  build_labs: string[];
  test_origins: string[];
  test_labs: string[];
};

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
