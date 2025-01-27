import { z } from 'zod';

import type {
  BuildsTabBuild,
  BuildStatus,
  StatusCount,
  TestHistory,
} from '@/types/general';
import type { BuildSummary, TestSummary } from '@/types/tree/TreeDetails';

type TTreesStatusSummary = {
  builds: Partial<BuildStatus>;
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

export type HardwareSummary = {
  builds: BuildSummary;
  boots: TestSummary;
  tests: TestSummary;
  trees: Trees[];
  configs: string[];
  architectures: string[];
  compilers: string[];
  compatibles: string[];
};

export type HardwareDetailsSummaryResponse = {
  summary: HardwareSummary;
};

export type THardwareDetails = {
  builds: BuildsTabBuild[];
  tests: TestHistory[];
  boots: TestHistory[];
  summary: HardwareSummary;
};

export interface THardwareDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      BuildsTabBuild,
      'test_status' | 'misc' | 'valid' | 'tree_name' | 'tree_index'
    >]: BuildsTabBuild[K][];
  }> {
  valid?: string[];
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
