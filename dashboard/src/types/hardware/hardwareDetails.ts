import { z } from 'zod';

import type { BuildsTabBuild, StatusCount, TestHistory } from '@/types/general';

import type {
  GlobalFilters,
  LocalFilters,
  Summary,
} from '@/types/commonDetails';

type TTreesStatusSummary = {
  builds: StatusCount;
  boots: StatusCount;
  tests: StatusCount;
};

export type Trees = {
  tree_name?: string;
  git_repository_branch?: string;
  git_repository_url?: string;
  head_git_commit_name?: string;
  head_git_commit_hash?: string;
  head_git_commit_tags?: string[];
  selected_commit_status?: TTreesStatusSummary;
  index: string;
};

export type PreparedTrees = Trees & {
  selectableCommits: CommitHistory[];
  isCommitHistoryDataLoading: boolean;
  isMainPageLoading: boolean;
};

type HardwareCommon = {
  trees: Trees[];
  compatibles: string[];
};

interface HardwareTestLocalFilters extends LocalFilters {
  platforms: string[];
}

type HardwareDetailsFilters = {
  all: GlobalFilters;
  builds: LocalFilters;
  boots: HardwareTestLocalFilters;
  tests: HardwareTestLocalFilters;
};

export type HardwareDetailsSummary = {
  summary: Summary;
  filters: HardwareDetailsFilters;
  common: HardwareCommon;
};

export type THardwareDetails = {
  builds: BuildsTabBuild[];
  tests: TestHistory[];
  boots: TestHistory[];
  summary: Summary;
  filters: HardwareDetailsFilters;
  common: HardwareCommon;
};

export interface THardwareDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      BuildsTabBuild,
      'test_status' | 'misc' | 'status' | 'tree_name' | 'tree_index'
    >]: BuildsTabBuild[K][];
  }> {
  status?: string[];
}

export const zTreeCommits = z.record(z.string()).default({});
export type TTreeCommits = z.infer<typeof zTreeCommits>;

export type CommitHead = {
  treeName: string;
  repositoryUrl: string;
  branch: string;
  commitHash: string;
};

export type CommitHistory = {
  git_commit_hash: string;
  git_repository_branch: string;
  git_repository_url: string;
  git_commit_tags: string[];
  git_commit_name: string;
  start_time: string;
  tree_name: string;
};

export type CommitHistoryTable = Record<string, CommitHistory[]>;

export type CommitHistoryResponse = {
  commit_history_table: CommitHistoryTable;
};
