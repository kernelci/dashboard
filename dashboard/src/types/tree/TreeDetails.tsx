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

export type BuildsTab = {
  builds: BuildsTabBuild[];
  summary: {
    builds: BuildStatus;
    configs: Record<string, BuildStatus>;
    architectures: Architecture;
  };
  issues: TIssue[];
  failedWithUnknownIssues: number;
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

export type TTreeTestsFullData = {
  bootArchSummary: ArchCompilerStatus[];
  testArchSummary: ArchCompilerStatus[];
  bootFailReasons: ErrorMessageCounts;
  testFailReasons: ErrorMessageCounts;
  testPlatformsWithErrors: string[];
  bootPlatformsFailing: string[];
  testConfigs: PropertyStatusCounts;
  bootConfigs: PropertyStatusCounts;
  testStatusSummary: StatusCounts;
  bootStatusSummary: StatusCounts;
  bootHistory: TestHistory[];
  testHistory: TestHistory[];
  bootIssues: TIssue[];
  testIssues: TIssue[];
  testEnvironmentCompatible: PropertyStatusCounts;
  bootEnvironmentCompatible: PropertyStatusCounts;
  hardwareUsed: string[];
  failedTestsWithUnknownIssues: number;
  failedBootsWithUnknownIssues: number;
  builds: BuildsTabBuild[];
  buildsSummary: {
    builds: BuildStatus;
    configs: Record<string, BuildStatus>;
    architectures: Architecture;
  };
  buildsIssues: TIssue[];
  failedBuildsWithUnknownIssues: number;
  treeUrl: string;
};

const possibleTabs = ['global.builds', 'global.boots', 'global.tests'] as const;

export const zPossibleTabValidator = z
  .enum(possibleTabs)
  .catch('global.builds');

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

export const zBuildsTableFilterValidator = z
  .enum(possibleBuildsTableFilter)
  .catch('all');
export const zTestsTableFilterValidator = z
  .enum(possibleTestsTableFilter)
  .catch('all');

export type BuildsTableFilter = z.infer<typeof zBuildsTableFilterValidator>;
export type TestsTableFilter = z.infer<typeof zTestsTableFilterValidator>;

export const zTableFilterInfo = object({
  buildsTable: zBuildsTableFilterValidator,
  bootsTable: zTestsTableFilterValidator,
  testsTable: zTestsTableFilterValidator,
});

export const zTableFilterInfoValidator = zTableFilterInfo.catch({
  buildsTable: zBuildsTableFilterValidator.parse(''),
  bootsTable: zTestsTableFilterValidator.parse(''),
  testsTable: zTestsTableFilterValidator.parse(''),
});

export type TableFilter = z.infer<typeof zTableFilterInfo>;

export const zTreeInformation = z
  .object({
    gitBranch: z.string().optional().catch(''),
    gitUrl: z.string().optional().catch(''),
    treeName: z.string().optional().catch(''),
    commitName: z.string().optional().catch(''),
    headCommitHash: z.string().optional().catch(undefined),
  })
  .catch({});

export type TestByCommitHash = {
  id: string;
  path: string | null;
  status: Status;
  duration: string;
  startTime: string;
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
