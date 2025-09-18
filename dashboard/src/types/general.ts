import { z, type ZodTypeAny } from 'zod';

import { DEFAULT_LISTING_ITEMS } from '@/utils/constants/general';

import type { Status } from './database';
import type { TTreeDetailsFilter } from './tree/TreeDetails';
import type { THardwareDetailsFilter } from './hardware/hardwareDetails';

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
  path?: string;
  status?: Status;
  start_time?: string;
  duration?: string;
  hardware?: string[];
  treeBranch?: string;
};

interface IEnvironmentMisc {
  platform?: string;
}

export type TreeBranchItem = {
  tree_name?: string;
  git_repository_branch?: string;
};

export type TestHistory = TreeBranchItem & {
  start_time?: string;
  status: Status;
  path?: string;
  id: string;
  duration?: number;
  environment_compatible?: string[];
  environment_misc?: IEnvironmentMisc;
};

// TODO: make other endpoints also return the test origin and combine this type with TestHistory
export type TestHistoryWithOrigin = TestHistory & {
  origin: string;
};

/**
 * @deprecated Use a more generic approach to the misc field.
 */
interface ITreeDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}

export type BuildsTabBuild = {
  id: string;
  origin: string;
  architecture: string;
  config_name: string;
  status: Status;
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
  | 'status'
  | 'start_time'
  | 'duration'
  | 'compiler'
  | 'log_url'
  | 'tree_name'
  | 'git_repository_branch'
>;

export type StatusCount = {
  PASS?: number;
  FAIL?: number;
  MISS?: number;
  SKIP?: number;
  ERROR?: number;
  NULL?: number;
  DONE?: number;
};

export type RequiredStatusCount = Required<StatusCount>;

export type Architecture = Record<
  string,
  RequiredStatusCount & {
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

export type PropertyStatusCounts = Record<string, StatusCounts>;

export type ArchCompilerStatus = {
  arch: string;
  compiler: string;
  status: StatusCounts;
};

export const zListingSize = z
  .optional(z.number().min(1).catch(DEFAULT_LISTING_ITEMS))
  .default(DEFAULT_LISTING_ITEMS);

const zIntervalInDaysUncatched = z.number().min(1);

export const makeZIntervalInDays = (
  defaultValue: number,
): z.ZodCatch<z.ZodNumber> => zIntervalInDaysUncatched.catch(defaultValue);

export const DEFAULT_ORIGIN = 'maestro';
export const zOrigin = z.string().default(DEFAULT_ORIGIN).catch(DEFAULT_ORIGIN);

const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'origins',
  'configs',
  'archs',
  'compilers',
  'buildStatus',
  'bootStatus',
  'testStatus',
  'hardware',
  'trees',
  'testPath',
  'bootPath',
  'buildIssue',
  'bootIssue',
  'testIssue',
  'issueCategories',
  'issueOptions',
  'issueCulprits',
  'buildOrigin',
  'bootOrigin',
  'testOrigin',
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
      origins: zFilterBoolValue,
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
      buildIssue: zFilterBoolValue,
      bootIssue: zFilterBoolValue,
      testIssue: zFilterBoolValue,
      issueCategories: zFilterBoolValue,
      issueOptions: zFilterBoolValue,
      issueCulprits: zFilterBoolValue,
      buildOrigin: zFilterBoolValue,
      bootOrigin: zFilterBoolValue,
      testOrigin: zFilterBoolValue,
    } satisfies Record<TFilterKeys, unknown>),
    z.record(z.never()),
  ])
  .default(DEFAULT_DIFF_FILTER)
  .catch(DEFAULT_DIFF_FILTER);

export type TFilter = z.infer<typeof zDiffFilter>;
export type TFilterObjectsKeys = z.infer<typeof zFilterObjectsKeys>;
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
  | 'listingSize'
  | 'hardwareSearch'
  | 'issueSearch'
  | 'treeInfo'
  | 'treeIndexes'
  | 'treeCommits'
  | 'startTimestampInSeconds'
  | 'endTimestampInSeconds'
  | 'issueVersion'
  | 'logOpen';
export type SearchSchema = Partial<Record<SearchParamsKeys, ZodTypeAny>>;

const requestFilters = {
  hardwareDetails: [
    'hardwareDetails.trees',
    'hardwareDetails.config_name',
    'hardwareDetails.architecture',
    'hardwareDetails.compiler',
    'hardwareDetails.duration_[gte]',
    'hardwareDetails.duration_[lte]',
  ],
  treeDetails: [
    'treeDetails.config_name',
    'treeDetails.architecture',
    'treeDetails.compiler',
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
    'build.status',
    'build.origin',
    'boot.origin',
    'test.origin',
  ],
  issueListing: [
    'origin',
    'issue.culprit',
    'issue.categories',
    'issue.options',
  ],
} as const;

type TRequestFiltersKey = keyof typeof requestFilters;
export type TRequestFiltersValues =
  (typeof requestFilters)[TRequestFiltersKey][number];

// Maps from fields that must be send to the request
// to field names used in the filter components
export const filterFieldMap = {
  'hardwareDetails.config_name': 'configs',
  'hardwareDetails.architecture': 'archs',
  'hardwareDetails.compiler': 'compilers',
  'hardwareDetails.duration_[gte]': 'buildDurationMin',
  'hardwareDetails.duration_[lte]': 'buildDurationMax',
  'hardwareDetails.trees': 'trees',
  'treeDetails.config_name': 'configs',
  'treeDetails.architecture': 'archs',
  'treeDetails.compiler': 'compilers',
  'treeDetails.duration_[gte]': 'buildDurationMin',
  'treeDetails.duration_[lte]': 'buildDurationMax',
  'boot.status': 'bootStatus',
  'boot.origin': 'bootOrigin',
  'boot.duration_[gte]': 'bootDurationMin',
  'boot.duration_[lte]': 'bootDurationMax',
  'test.status': 'testStatus',
  'test.origin': 'testOrigin',
  'test.duration_[gte]': 'testDurationMin',
  'test.duration_[lte]': 'testDurationMax',
  'test.hardware': 'hardware',
  'test.path': 'testPath',
  'boot.path': 'bootPath',
  'build.issue': 'buildIssue',
  'boot.issue': 'bootIssue',
  'test.issue': 'testIssue',
  'build.status': 'buildStatus',
  'build.origin': 'buildOrigin',
  origin: 'origins',
  'issue.culprit': 'issueCulprits',
  'issue.categories': 'issueCategories',
  'issue.options': 'issueOptions',
} as const satisfies Record<TRequestFiltersValues, TFilterKeys>;

/**
 * Maps a requestFilter
 *
 * as THardwareDetailsFilter | TTreeDetailsFilter
 * from {'treeDetails.config_name': ["value"]}
 * to {'config_name': ["value"]}
 *
 * or as a TFilter
 * from {'treeDetails.config_name': {'value1': true, 'value2': true}}
 * to {'config_name': ['value1', 'value2']}
 *
 * If the target filter is test or issueListing, the prefix won't be removed
 * (such as *test* in "test.hardware" or *boot* in "boot.path")
 */
export const getTargetFilter = (
  requestFilter: THardwareDetailsFilter | TTreeDetailsFilter | TFilter,
  target: TRequestFiltersKey,
): THardwareDetailsFilter | TTreeDetailsFilter => {
  const targetFilter: readonly string[] = requestFilters[target];
  const accumulator: Record<
    string,
    THardwareDetailsFilter | TTreeDetailsFilter
  > = {};

  Object.entries(requestFilter).forEach(([k, v]) => {
    if (!targetFilter.includes(k)) {
      return;
    }

    // TFilter has its values as Record<string, boolean>, while the other types are a direct array.
    // So in the case that v is a Record, the values that we want are the keys of that record.
    if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
      v = Object.keys(v);
    }

    const splitted = k.split('.');
    const field = splitted[splitted.length - 1];
    if (target === 'test' || target === 'issueListing') {
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
  Issues = 'issues',
}

export type PossibleMonitorPath = '/tree' | '/hardware' | '/issues';
