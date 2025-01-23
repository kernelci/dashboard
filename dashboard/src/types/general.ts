import { z, type ZodTypeAny } from 'zod';

import type { Status } from './database';
import type { TTreeDetailsFilter } from './tree/TreeDetails';
import type { THardwareDetailsFilter } from './hardware/hardwareDetails';
type IncidentsInfo = { incidentsCount: number };
export type TPathTests = {
  path_group: string;
  fail_tests: number;
  error_tests: number;
  miss_tests: number;
  pass_tests: number;
  done_tests: number;
  skip_tests: number;
  null_tests: number;
  total_tests: number;
  individual_tests: TIndividualTest[];
};

export type TIndividualTest = {
  id: string;
  path: string;
  status?: Status;
  start_time: string;
  duration: string;
  hardware?: string[];
};

export type TIssue = {
  id: string;
  version: string;
  comment?: string;
  report_url?: string;
  incidents_info: IncidentsInfo;
};

export type TestHistory = {
  start_time: string;
  status: Status;
  path: string;
  id: string;
  duration?: number;
  environment_compatible?: string[];
};

interface ITreeDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}

export type BuildsTabBuild = {
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
  misc: ITreeDetailsMisc | null;
  tree_name?: string;
  tree_index?: number;
};

export type BuildsTableBuild = Pick<
  BuildsTabBuild,
  | 'id'
  | 'architecture'
  | 'config_name'
  | 'valid'
  | 'start_time'
  | 'duration'
  | 'compiler'
  | 'log_url'
>;

export type BuildStatus = {
  valid: number;
  invalid: number;
  null: number;
};

export interface StatusCount {
  PASS?: number;
  FAIL?: number;
  MISS?: number;
  SKIP?: number;
  ERROR?: number;
  NULL?: number;
  DONE?: number;
}

export type Architecture = Record<
  string,
  BuildStatus & {
    compilers: string[];
  }
>;

export type ResponseData<T> = T & {
  error?: string;
};

/**
 * @deprecated use StatusCount
 */
export type StatusCounts = {
  [key in Status]: number | undefined;
};

export type ArchCompilerStatus = {
  arch: string;
  compiler: string;
  status: StatusCounts;
};

const zIntervalInDaysUncatched = z.number().min(1);

export const makeZIntervalInDays = (
  defaultValue: number,
): z.ZodCatch<z.ZodNumber> => zIntervalInDaysUncatched.catch(defaultValue);

const origins = [
  '0dayci',
  'broonie',
  'maestro',
  'microsoft',
  'redhat',
  'syzbot',
  'tuxsuite',
] as const;
export const DEFAULT_ORIGIN = 'maestro';

export type TOrigins = (typeof origins)[number];

export const zOriginEnum = z.enum(origins);
export const zOrigin = zOriginEnum
  .default(DEFAULT_ORIGIN)
  .catch(DEFAULT_ORIGIN);

const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'configs',
  'archs',
  'compilers',
  'buildStatus',
  'bootStatus',
  'testStatus',
  'hardware',
  'trees',
  'bootPlatform',
  'testPlatform',
  'testPath',
  'bootPath',
  'buildIssue',
  'bootIssue',
  'testIssue',
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

export const DEFAULT_DIFF_FILTER = {};
export const zDiffFilter = z
  .union([
    z.object({
      configs: zFilterBoolValue,
      archs: zFilterBoolValue,
      buildStatus: zFilterBoolValue,
      compilers: zFilterBoolValue,
      bootStatus: zFilterBoolValue,
      testStatus: zFilterBoolValue,
      testPath: zFilterBoolValue,
      bootPath: zFilterBoolValue,
      buildDurationMax: zFilterNumberValue,
      buildDurationMin: zFilterNumberValue,
      bootDurationMin: zFilterNumberValue,
      bootDurationMax: zFilterNumberValue,
      testDurationMin: zFilterNumberValue,
      testDurationMax: zFilterNumberValue,
      hardware: zFilterBoolValue,
      trees: zFilterBoolValue,
      bootPlatform: zFilterBoolValue,
      testPlatform: zFilterBoolValue,
      buildIssue: zFilterBoolValue,
      bootIssue: zFilterBoolValue,
      testIssue: zFilterBoolValue,
    } satisfies Record<TFilterKeys, unknown>),
    z.record(z.never()),
  ])
  .default(DEFAULT_DIFF_FILTER)
  .catch(DEFAULT_DIFF_FILTER);

export type TFilterObjectsKeys = z.infer<typeof zFilterObjectsKeys>;
export type TFilter = z.infer<typeof zDiffFilter>;
export type TFilterNumberKeys = z.infer<typeof zFilterNumberKeys>;

export const isTFilterObjectKeys = (key: string): key is TFilterObjectsKeys => {
  return zFilterObjectsKeys.safeParse(key).success;
};

export const isTFilterNumberKeys = (key: string): key is TFilterNumberKeys => {
  return zFilterNumberKeys.safeParse(key).success;
};

export type SearchParamsKeys =
  | 'origin'
  | 'intervalInDays'
  | 'currentPageTab'
  | 'tableFilter'
  | 'diffFilter'
  | 'treeSearch'
  | 'hardwareSearch'
  | 'treeInfo'
  | 'treeIndexes'
  | 'treeCommits'
  | 'startTimestampInSeconds'
  | 'endTimestampInSeconds';
export type SearchSchema = Partial<Record<SearchParamsKeys, ZodTypeAny>>;

const requestFilters = {
  hardwareDetails: [
    'hardwareDetails.trees',
    'hardwareDetails.config_name',
    'hardwareDetails.architecture',
    'hardwareDetails.compiler',
    'hardwareDetails.valid',
    'hardwareDetails.duration_[gte]',
    'hardwareDetails.duration_[lte]',
  ],
  treeDetails: [
    'treeDetails.config_name',
    'treeDetails.architecture',
    'treeDetails.compiler',
    'treeDetails.valid',
    'treeDetails.duration_[gte]',
    'treeDetails.duration_[lte]',
  ],
  test: [
    'test.status',
    'test.duration_[gte]',
    'test.duration_[lte]',
    'test.hardware',
    'test.path',
    'boot.path',
    'boot.status',
    'boot.duration_[gte]',
    'boot.duration_[lte]',
    'build.issue',
    'test.issue',
    'boot.issue',
    'boot.platform',
    'test.platform',
  ],
} as const;

type TRequestFiltersKey = keyof typeof requestFilters;
export type TRequestFiltersValues =
  (typeof requestFilters)[TRequestFiltersKey][number];

export const filterFieldMap = {
  'hardwareDetails.config_name': 'configs',
  'hardwareDetails.architecture': 'archs',
  'hardwareDetails.compiler': 'compilers',
  'hardwareDetails.valid': 'buildStatus',
  'hardwareDetails.duration_[gte]': 'buildDurationMin',
  'hardwareDetails.duration_[lte]': 'buildDurationMax',
  'hardwareDetails.trees': 'trees',
  'treeDetails.config_name': 'configs',
  'treeDetails.architecture': 'archs',
  'treeDetails.compiler': 'compilers',
  'treeDetails.valid': 'buildStatus',
  'treeDetails.duration_[gte]': 'buildDurationMin',
  'treeDetails.duration_[lte]': 'buildDurationMax',
  'boot.status': 'bootStatus',
  'boot.duration_[gte]': 'bootDurationMin',
  'boot.duration_[lte]': 'bootDurationMax',
  'test.status': 'testStatus',
  'test.duration_[gte]': 'testDurationMin',
  'test.duration_[lte]': 'testDurationMax',
  'test.hardware': 'hardware',
  'test.path': 'testPath',
  'boot.path': 'bootPath',
  'build.issue': 'buildIssue',
  'boot.issue': 'bootIssue',
  'test.issue': 'testIssue',
  'boot.platform': 'bootPlatform',
  'test.platform': 'testPlatform',
} as const satisfies Record<TRequestFiltersValues, TFilterKeys>;

export const getTargetFilter = (
  filter: THardwareDetailsFilter | TTreeDetailsFilter | TFilter,
  target: TRequestFiltersKey,
): THardwareDetailsFilter | TTreeDetailsFilter => {
  const targetFilter: readonly string[] = requestFilters[target];
  const accumulator: Record<
    string,
    THardwareDetailsFilter | TTreeDetailsFilter
  > = {};

  Object.entries(filter).forEach(([k, v]) => {
    if (!targetFilter.includes(k)) return;

    const splitted = k.split('.');
    const field = splitted[splitted.length - 1];
    if (target === 'test') {
      accumulator[k] = v;
    } else {
      accumulator[field] = v;
    }
  });

  return accumulator;
};

export enum RedirectFrom {
  Tree = 'tree',
  Hardware = 'hardware',
}
