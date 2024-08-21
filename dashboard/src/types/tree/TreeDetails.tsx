import { z } from 'zod';

import { MessagesKey } from '@/locales/messages';

import type { ErrorStatus, Status } from '../database';

type TreeDetailsBuild = {
  id: string;
  architecture: string;
  config_name: string;
  valid: boolean;
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
  buildTime?: string;
  status?: 'valid' | 'invalid';
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

const possibleTableFilter = ['error', 'success', 'all'] as const;

export const zTableFilterValidator = z.enum(possibleTableFilter).catch('all');

export type TableFilter = z.infer<typeof zTableFilterValidator>;

const zFilterValue = z.record(z.boolean()).optional();
export type TFilterValues = z.infer<typeof zFilterValue>;

const filterKeys = ['branches', 'configs', 'archs', 'status'] as const;
export type TFilterKeys = (typeof filterKeys)[number];

export const zDiffFilter = z
  .union([
    z.object({
      branches: zFilterValue,
      configs: zFilterValue,
      archs: zFilterValue,
      status: zFilterValue,
    } satisfies Record<TFilterKeys, unknown>),
    z.record(z.never()),
  ])
  .catch({});

export type TFilter = z.infer<typeof zDiffFilter>;

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
