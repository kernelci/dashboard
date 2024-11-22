import { z } from 'zod';

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
  failedWithUnknownIssues: number;
};

type Tests = {
  archSummary: ArchCompilerStatus[];
  history: TestHistory[];
  platformsFailing: string[];
  statusSummary: StatusCounts;
  failReasons: Record<string, unknown>;
  configs: Record<string, StatusCounts>;
  issues: TIssue[];
  failedWithUnknownIssues: number;
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

// TODO: move to general types
const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'configs',
  'archs',
  'compilers',
  'buildStatus',
  'bootStatus',
  'testStatus',
  'trees',
  'path',
  'bootPath',
  'testPath',
]);
export const zFilterNumberKeys = z.enum([
  'buildDurationMin',
  'buildDurationMax',
  'bootDurationMin',
  'bootDurationMax',
  'testDurationMin',
  'testDurationMax',
]);

export type TFilterKeys =
  | z.infer<typeof zFilterObjectsKeys>
  | z.infer<typeof zFilterNumberKeys>;

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
      trees: zFilterBoolValue,
      path: zFilterBoolValue,
      bootPath: zFilterBoolValue,
      testPath: zFilterBoolValue,
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

// TODO remove eslint disable rules
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const requestFilters = {
  hardwareDetails: [
    'hardwareDetails.trees',
    'hardwareDetails.config_name',
    'hardwareDetails.architecture',
    'hardwareDetails.compiler',
    'hardwareDetails.valid',
    'hardwareDetails.duration_[gte]',
    'hardwareDetails.duration_[lte]',
    'test.status',
    'test.duration_[gte]',
    'test.duration_[lte]',
    'boot.status',
    'boot.duration_[gte]',
    'boot.duration_[lte]',
    'test.path',
    'boot.path',
  ],
} as const;

type TRequestFiltersKey = keyof typeof requestFilters;
export type TRequestFiltersValues =
  (typeof requestFilters)[TRequestFiltersKey][number];

export interface THardwareDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      BuildsTabBuild,
      'test_status' | 'misc' | 'valid' | 'tree_name' | 'tree_index'
    >]: BuildsTabBuild[K][];
  }> {
  valid?: string[];
}

export const getTargetFilter = (
  filter: THardwareDetailsFilter,
  target: TRequestFiltersKey,
): THardwareDetailsFilter => {
  const targetFilter: readonly string[] = requestFilters[target];
  const acc: Record<string, unknown> = {}; //fix this

  Object.entries(filter).forEach(([k, v]) => {
    if (!targetFilter.includes(k)) return;

    const splitted = k.split('.');
    const field = splitted[splitted.length - 1];
    if (splitted[0] !== 'hardwareDetails') {
      acc[k] = v;
    } else {
      acc[field] = v;
    }
  });

  return acc;
};
