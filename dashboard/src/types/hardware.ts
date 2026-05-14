import type {
  RequiredStatusCount,
  ShortStatusCount,
  StatusCount,
} from './general';

export type HardwareItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: RequiredStatusCount;
  test_status_summary: StatusCount;
  boot_status_summary: StatusCount;
};

export interface HardwareListingResponse {
  hardware: HardwareItem[];
}

export type HardwareItemV2 = {
  hardware?: string[];
  platform: string;
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
};

export interface HardwareListingResponseV2 {
  hardware: HardwareItemV2[];
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
