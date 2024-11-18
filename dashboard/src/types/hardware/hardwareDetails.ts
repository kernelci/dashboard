import type {
  ArchCompilerStatus,
  BuildsTabBuild,
  BuildStatus,
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
};

type Tests = {
  archSummary: ArchCompilerStatus[];
  history: TestHistory[];
  platformsFailing: string[];
  statusSummary: StatusCounts;
  failReasons: Record<string, unknown>;
  configs: Record<string, StatusCounts>;
  issues: TIssue[];
};

export type Trees = {
  treeName?: string;
  gitRepositoryBranch?: string;
  gitRepositoryUrl?: string;
  headGitCommitName?: string;
  headGitCommitHash?: string;
  index: string;
};
export type THardwareDetails = {
  builds: BuildsData;
  tests: Tests;
  boots: Tests;
  trees: Trees[];
};
