import { z } from 'zod';

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
    builds: Results;
    configs: object;
    architectures: object;
  };
};

export type Results = {
  valid: number;
  invalid: number;
  null: number;
};
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

type ConfigCounts = {
  [key: string]: number;
};

type ErrorCountPerArchitecture = {
  [key: string]: number;
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

export type TTreeTestsData = {
  statusCounts: StatusCounts;
  errorCounts: ErrorCounts;
  configCounts: ConfigCounts;
  testHistory: TestHistory[];
  errorCountPerArchitecture: ErrorCountPerArchitecture;
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

export const possibleTableFilter = ['error', 'success', 'all'] as const;

export const zTableFilterValidator = z.enum(possibleTableFilter).catch('all');

export type TableFilter = z.infer<typeof zTableFilterValidator>;

const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'branches',
  'configs',
  'archs',
  'status',
  'bootStatus',
  'testStatus',
]);
export const zFilterNumberKeys = z.enum(['duration_min', 'duration_max']);
const filterKeys = [
  ...zFilterObjectsKeys.options,
  ...zFilterNumberKeys.options,
] as const;

export type TFilterKeys = (typeof filterKeys)[number];

export const zDiffFilter = z
  .union([
    z.object({
      branches: zFilterBoolValue,
      configs: zFilterBoolValue,
      archs: zFilterBoolValue,
      status: zFilterBoolValue,
      bootStatus: zFilterBoolValue,
      testStatus: zFilterBoolValue,
      duration_min: zFilterNumberValue,
      duration_max: zFilterNumberValue,
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
  })
  .catch({});

export type TestByCommitHash = {
  id: string;
  architecture: string | null;
  compiler: string | null;
  path: string | null;
  status: string;
};

export type TTestByCommitHashResponse = {
  tests: TestByCommitHash[];
};
