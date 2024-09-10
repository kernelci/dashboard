import { object, z } from 'zod';

import { ReactNode } from 'react';

import { MessagesKey } from '@/locales/messages';

import type { ErrorStatus, Status } from '../database';

export type TreeDetailsBuild = {
  id: string;
  architecture: string;
  config_name: string;
  valid: boolean | null;
  start_time: string;
  duration: string;
  compiler: string;
  config_url: string;
  log_url: string;
  git_repository_branch: string;
  git_repository_url: string;
  status: {
    fail_tests: number;
    error_tests: number;
    miss_tests: number;
    pass_tests: number;
    done_tests: number;
    skip_tests: number;
    null_tests: number;
    total_tests: number;
  };
  misc: ITreeDetailsMisc | null;
};

interface ITreeDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}

export type AccordionItemBuilds = {
  id: string;
  config?: string;
  compiler?: string;
  date?: string;
  buildErrors?: number;
  buildTime?: string | ReactNode;
  status?: 'valid' | 'invalid' | 'null';
  testStatus?: {
    failTests: number;
    errorTests: number;
    passTests: number;
    skipTests: number;
    missTests: number;
    doneTests: number;
  };
  kernelImage?: string;
  buildLogs?: string;
  kernelConfig?: string;
  dtb?: string;
  systemMap?: string;
  modules?: string;
};

export type TreeDetails = {
  builds: TreeDetailsBuild[];
  summary: {
    builds: BuildStatus;
    configs: Record<string, BuildStatus>;
    architectures: TArch;
  };
};

export type BuildStatus = {
  valid: number;
  invalid: number;
  null: number;
};

type TArch = Record<
  string,
  BuildStatus & {
    compilers: string[];
  }
>;

export interface TTreeDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      TreeDetailsBuild,
      'test_status' | 'misc' | 'valid'
    >]: TreeDetailsBuild[K][];
  }> {
  valid?: string[];
}

type TestHistory = {
  start_time: string;
  status: string;
};

type ErrorCounts = {
  [key in ErrorStatus]: number | undefined;
};

type CompilersPerArchitecture = {
  [key: string]: string[];
};

type ErrorMessageCounts = {
  [key: string]: number;
};

type StatusCounts = {
  [key in Status]: number | undefined;
};

type PropertyStatusCounts = Record<string, StatusCounts>;

export type TTreeTestsData = {
  statusCounts: StatusCounts;
  errorCounts: ErrorCounts;
  configStatusCounts: PropertyStatusCounts;
  testHistory: TestHistory[];
  architectureStatusCounts: PropertyStatusCounts;
  compilersPerArchitecture: CompilersPerArchitecture;
  platformsWithError: string[];
  errorMessageCounts: ErrorMessageCounts;
};

export type PossibleTabs = Extract<
  MessagesKey,
  'treeDetails.builds' | 'treeDetails.boots' | 'treeDetails.tests'
>;

const possibleTabs = [
  'treeDetails.builds',
  'treeDetails.boots',
  'treeDetails.tests',
] as const satisfies PossibleTabs[];

export const zPossibleValidator = z
  .enum(possibleTabs)
  .catch('treeDetails.boots');

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

const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'configs',
  'archs',
  'compilers',
  'buildStatus',
  'bootStatus',
  'testStatus',
]);
export const zFilterNumberKeys = z.enum([
  'buildDurationMin',
  'buildDurationMax',
  'bootDurationMin',
  'bootDurationMax',
  'testDurationMin',
  'testDurationMax',
]);
const filterKeys = [
  ...zFilterObjectsKeys.options,
  ...zFilterNumberKeys.options,
] as const;

export type TFilterKeys = (typeof filterKeys)[number];

export const zDiffFilter = z
  .union([
    z.object({
      configs: zFilterBoolValue,
      archs: zFilterBoolValue,
      buildStatus: zFilterBoolValue,
      compilers: zFilterBoolValue,
      bootStatus: zFilterBoolValue,
      testStatus: zFilterBoolValue,
      buildDurationMax: zFilterNumberValue,
      buildDurationMin: zFilterNumberValue,
      bootDurationMin: zFilterNumberValue,
      bootDurationMax: zFilterNumberValue,
      testDurationMin: zFilterNumberValue,
      testDurationMax: zFilterNumberValue,
    } satisfies Record<TFilterKeys, unknown>),
    z.record(z.never()),
  ])
  .catch({});

export type TFilter = z.infer<typeof zDiffFilter>;
export type TFilterObjectsKeys = z.infer<typeof zFilterObjectsKeys>;
export type TFilterNumberKeys = z.infer<typeof zFilterNumberKeys>;

export const isTFilterObjectKeys = (key: string): key is TFilterObjectsKeys => {
  return zFilterObjectsKeys.safeParse(key).success;
};

export const isTFilterNumberKeys = (key: string): key is TFilterNumberKeys => {
  return zFilterNumberKeys.safeParse(key).success;
};

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
  };
  non_boots_tests: {
    fail_count: number;
    error_count: number;
    miss_count: number;
    pass_count: number;
    done_count: number;
    skip_count: number;
  };
};

export type TTreeCommitHistoryResponse = PaginatedCommitHistoryByTree[];
