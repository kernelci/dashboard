import { object, z } from 'zod';

import type { ReactNode } from 'react';

import type {
  BuildsTabBuild,
  BuildStatus,
  Architecture,
  TestHistory,
  TIssue,
  StatusCounts,
  ArchCompilerStatus,
} from '@/types/general';

import type { Status } from '@/types/database';

export type AccordionItemBuilds = {
  id: string;
  config?: string;
  architecture?: string;
  compiler?: string;
  date?: string;
  buildErrors?: number;
  buildTime?: string | ReactNode;
  status: 'valid' | 'invalid' | 'null';
  kernelImage?: string;
  buildLogs?: string;
  kernelConfig?: string;
  dtb?: string;
  systemMap?: string;
  modules?: string;
  treeBranch?: string;
};

export interface TTreeDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      BuildsTabBuild,
      'test_status' | 'misc' | 'valid' | 'tree_name' | 'tree_index'
    >]: BuildsTabBuild[K][];
  }> {
  valid?: string[];
}

type CompilersPerArchitecture = {
  [key: string]: string[];
};

type ErrorMessageCounts = {
  [key: string]: number;
};

type PropertyStatusCounts = Record<string, StatusCounts>;

export type TTreeTestsData = {
  statusCounts: StatusCounts;
  configStatusCounts: PropertyStatusCounts;
  testHistory: TestHistory[];
  architectureStatusCounts: PropertyStatusCounts;
  compilersPerArchitecture: CompilersPerArchitecture;
  platformsWithError: string[];
  errorMessageCounts: ErrorMessageCounts;
  environmentCompatible: PropertyStatusCounts;
};

export type TestSummary = {
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

export type BuildSummary = {
  status: BuildStatus;
  architectures: Architecture;
  configs: Record<string, BuildStatus>;
  issues: TIssue[];
  unknown_issues: number;
};

type TreeSummary = {
  boots: TestSummary;
  builds: BuildSummary;
  tests: TestSummary;
};

type TreeCommon = {
  hardware: string[];
  tree_url: string;
  git_commit_tags: string[];
};

type TreeGlobalFilters = {
  configs: string[];
  architectures: string[];
  compilers: string[];
};

type TreeLocalFilters = {
  issues: string[];
};

type TreeFilters = {
  all: TreeGlobalFilters;
  builds: TreeLocalFilters;
  boots: TreeLocalFilters;
  tests: TreeLocalFilters;
};

export type TreeDetailsFullData = {
  builds: BuildsTabBuild[];
  boots: TestHistory[];
  tests: TestHistory[];
  summary: TreeSummary;
  common: TreeCommon;
  filters: TreeFilters;
};

export type TreeDetailsSummary = {
  summary: TreeSummary;
  common: TreeCommon;
  filters: TreeFilters;
};

export type TreeDetailsBuilds = {
  builds: BuildsTabBuild[];
};

export type TreeDetailsTests = {
  tests: TestHistory[];
};

export type TreeDetailsBoots = {
  boots: TestHistory[];
};

export const possibleTabs = [
  'global.builds',
  'global.boots',
  'global.tests',
] as const;

export const possibleBuildsTableFilter = [
  'invalid',
  'valid',
  'all',
  'null',
] as const;

export const possibleTestsTableFilter = [
  'all',
  'success',
  'failed',
  'inconclusive',
] as const;

export const defaultValidadorValues: {
  tab: (typeof possibleTabs)[number];
  buildsTableFilter: (typeof possibleBuildsTableFilter)[number];
  testsTableFilter: (typeof possibleTestsTableFilter)[number];
} = {
  tab: 'global.builds',
  buildsTableFilter: 'all',
  testsTableFilter: 'all',
};

export const zPossibleTabValidator = z
  .enum(possibleTabs)
  .default(defaultValidadorValues.tab)
  .catch(defaultValidadorValues.tab);

export type PossibleTabs = z.infer<typeof zPossibleTabValidator>;

export const zBuildsTableFilterValidator = z
  .enum(possibleBuildsTableFilter)
  .catch(defaultValidadorValues.buildsTableFilter);

export const zTestsTableFilterValidator = z
  .enum(possibleTestsTableFilter)
  .catch(defaultValidadorValues.testsTableFilter);

export type BuildsTableFilter = z.infer<typeof zBuildsTableFilterValidator>;
export type TestsTableFilter = z.infer<typeof zTestsTableFilterValidator>;

export const zTableFilterInfo = object({
  buildsTable: zBuildsTableFilterValidator,
  bootsTable: zTestsTableFilterValidator,
  testsTable: zTestsTableFilterValidator,
});

export const zTableFilterInfoDefault = {
  buildsTable: zBuildsTableFilterValidator.parse(''),
  bootsTable: zTestsTableFilterValidator.parse(''),
  testsTable: zTestsTableFilterValidator.parse(''),
};

export const zTableFilterInfoValidator = zTableFilterInfo
  .default(zTableFilterInfoDefault)
  .catch(zTableFilterInfoDefault);

export type TableFilter = z.infer<typeof zTableFilterInfo>;

export const DEFAULT_TREE_INFO = {};
export const zTreeInformationObject = z.object({
  gitBranch: z.string().optional().catch(''),
  gitUrl: z.string().optional().catch(''),
  treeName: z.string().optional().catch(''),
  commitName: z.string().optional().catch(''),
  headCommitHash: z.string().optional().catch(undefined),
});
export const zTreeInformation = zTreeInformationObject
  .default(DEFAULT_TREE_INFO)
  .catch(DEFAULT_TREE_INFO);

export type TTreeInformation = z.infer<typeof zTreeInformation>;

export type TestByCommitHash = {
  id: string;
  path: string | null;
  status: Status;
  duration: string;
  startTime: string;
  hardware?: string[];
};

export type TTestByCommitHashResponse = {
  tests: TestByCommitHash[];
};

export type PaginatedCommitHistoryByTree = {
  git_commit_hash: string;
  git_commit_name?: string;
  earliest_start_time: string;
  builds: {
    valid_builds: number;
    invalid_builds: number;
    null_builds: number;
  };
  boots_tests: {
    fail_count: number;
    error_count: number;
    miss_count: number;
    pass_count: number;
    done_count: number;
    skip_count: number;
    null_count: number;
  };
  non_boots_tests: {
    fail_count: number;
    error_count: number;
    miss_count: number;
    pass_count: number;
    done_count: number;
    skip_count: number;
    null_count: number;
  };
};

export type BuildCountsResponse = {
  log_excerpt?: string;
  build_counts: {
    build_id: string;
    fail_tests: number;
    error_tests: number;
    miss_tests: number;
    pass_tests: number;
    done_tests: number;
    skip_tests: number;
    null_tests: number;
    total_tests: number;
  };
};

export type LogFile = {
  specific_log_url: string;
  file_name: string;
  file_size: string;
  date: string;
};

export type LogFilesResponse = {
  log_files: LogFile[];
};

export type TTreeCommitHistoryResponse = PaginatedCommitHistoryByTree[];
