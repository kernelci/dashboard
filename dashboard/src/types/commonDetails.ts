import type {
  ArchCompilerStatus,
  Architecture,
  BuildStatus,
  PropertyStatusCounts,
  StatusCounts,
  TIssue,
} from './general';

type TestSummary = {
  status: StatusCounts;
  architectures: ArchCompilerStatus[];
  configs: PropertyStatusCounts;
  issues: TIssue[];
  unknown_issues: number;
  fail_reasons: Record<string, number>;
  failed_platforms: string[];
  environment_compatible?: PropertyStatusCounts;
  environment_misc?: PropertyStatusCounts;
  platforms?: PropertyStatusCounts;
};

type BuildSummary = {
  status: BuildStatus;
  architectures: Architecture;
  configs: Record<string, BuildStatus>;
  issues: TIssue[];
  unknown_issues: number;
};

export type Summary = {
  builds: BuildSummary;
  boots: TestSummary;
  tests: TestSummary;
};

export type GlobalFilters = {
  configs: string[];
  architectures: string[];
  compilers: string[];
};

export type IssueFilterItem = [string, number?];

export type LocalFilters = {
  issues: IssueFilterItem[];
};

export type DetailsFilters = {
  all: GlobalFilters;
  builds: LocalFilters;
  boots: LocalFilters;
  tests: LocalFilters;
};
