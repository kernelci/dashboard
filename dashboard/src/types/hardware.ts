import type { ShortStatusCount } from './general';

export type HardwareRegistryNamedLink = {
  id: string;
  url?: string | null;
  form_factor?: string | null;
};

export type HardwareRegistryProcessorInfo = {
  id: string;
  architecture?: string | null;
  cores?: number | null;
  max_clock_speed_mhz?: number | null;
  url?: string | null;
  description?: string | null;
};

export type HardwareRegistryInfo = {
  platform_id: string;
  board_type?: string | null;
  form_factor?: string | null;
  description?: string | null;
  url?: string | null;
  vendor?: HardwareRegistryNamedLink | null;
  silicon_vendor?: HardwareRegistryNamedLink | null;
  system_module?: HardwareRegistryNamedLink | null;
  processor?: HardwareRegistryProcessorInfo | null;
};

export type HardwareItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
  registry?: HardwareRegistryInfo | null;
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
