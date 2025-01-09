import { z } from 'zod';

import type {
  ArchCompilerStatus,
  BuildsTabBuild,
  BuildStatus,
  StatusCount,
  StatusCounts,
  TestHistory,
  TIssue,
} from '@/types/general';

type BuildSummary = {
  builds: BuildStatus;
  configs: Record<string, BuildStatus>;
  architectures: Record<
    string,
    {
      valid: number;
      invalid: number;
      null: number;
      compilers: string[];
    }
  >;
};

type BuildsData = {
  items: BuildsTabBuild[];
  issues: TIssue[];
  summary: BuildSummary;
  platforms: Record<string, BuildStatus>;
  failedWithUnknownIssues: number;
};

type Tests = {
  archSummary: ArchCompilerStatus[];
  history: TestHistory[];
  platforms: Record<string, StatusCount>;
  platformsFailing: string[];
  statusSummary: StatusCounts;
  failReasons: Record<string, unknown>;
  configs: Record<string, StatusCounts>;
  issues: TIssue[];
  failedWithUnknownIssues: number;
};

type TTreesStatusSummary = {
  builds: Partial<BuildStatus>;
  boots: StatusCount;
  tests: StatusCount;
};

export type Trees = {
  treeName?: string;
  gitRepositoryBranch?: string;
  gitRepositoryUrl?: string;
  headGitCommitName?: string;
  headGitCommitHash?: string;
  headGitCommitTags?: string[];
  selectedCommitStatusSummary?: TTreesStatusSummary;
  index: string;
};

export type PreparedTrees = Trees & {
  selectableCommits: CommitHistory[];
  isCommitHistoryDataLoading: boolean;
  isMainPageLoading: boolean;
};

export type THardwareDetails = {
  builds: BuildsData;
  tests: Tests;
  boots: Tests;
  trees: Trees[];
  configs: string[];
  archs: string[];
  compilers: string[];
  compatibles: string[];
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
  commitHistoryTable: CommitHistoryTable;
};
