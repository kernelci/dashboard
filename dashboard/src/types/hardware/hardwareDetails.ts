import type {
  BuildsTabBuild,
  BuildStatus,
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
  history: TestHistory[];
  platformsFailing: string[];
  statusSummary: Record<string, number>;
  failReasons: Record<string, unknown>;
  configs: Record<string, Record<string, number>>;
  issues: TIssue[];
};

export type THardwareDetails = {
  builds: BuildsData;
  tests: Tests;
  boots: Tests;
};
