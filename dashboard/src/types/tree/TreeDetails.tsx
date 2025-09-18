import { object, z } from 'zod';

import type { ReactNode } from 'react';

import type {
  BuildsTabBuild,
  TestHistory,
  StatusCounts,
  PropertyStatusCounts,
  RequiredStatusCount,
  TestHistoryWithOrigin,
} from '@/types/general';

import type { Status } from '@/types/database';
import type { DetailsFilters, Summary } from '@/types/commonDetails';

import type { TableTestStatus } from './Tree';

export type AccordionItemBuilds = {
  id: string;
  config?: string;
  architecture?: string;
  compiler?: string;
  date?: string;
  buildErrors?: number;
  buildTime?: string | ReactNode;
  status: Status;
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
      'test_status' | 'misc' | 'status' | 'tree_name' | 'tree_index'
    >]: BuildsTabBuild[K][];
  }> {
  status?: string[];
}

type CompilersPerArchitecture = {
  [key: string]: string[];
};

type ErrorMessageCounts = {
  [key: string]: number;
};

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

type TreeCommon = {
  hardware: string[];
  tree_url: string;
  git_commit_tags: string[];
};

export type TreeDetailsFullData = {
  builds: BuildsTabBuild[];
  boots: TestHistoryWithOrigin[];
  tests: TestHistoryWithOrigin[];
  summary: Summary;
  common: TreeCommon;
  filters: DetailsFilters;
};

export type TreeDetailsSummary = {
  summary: Summary;
  common: TreeCommon;
  filters: DetailsFilters;
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

export const possibleTableFilters = [
  'all',
  'success',
  'failed',
  'inconclusive',
] as const;

export const defaultValidadorValues: {
  tab: (typeof possibleTabs)[number];
  tableFilter: (typeof possibleTableFilters)[number];
} = {
  tab: 'global.builds',
  tableFilter: 'all',
};

export const zPossibleTabValidator = z
  .enum(possibleTabs)
  .default(defaultValidadorValues.tab)
  .catch(defaultValidadorValues.tab);

export type PossibleTabs = z.infer<typeof zPossibleTabValidator>;

export const zTableFilterValidator = z
  .enum(possibleTableFilters)
  .catch(defaultValidadorValues.tableFilter);

export type PossibleTableFilters = z.infer<typeof zTableFilterValidator>;

export const zTableFilterInfo = object({
  buildsTable: zTableFilterValidator,
  bootsTable: zTableFilterValidator,
  testsTable: zTableFilterValidator,
});

export const zTableFilterInfoDefault = {
  buildsTable: zTableFilterValidator.parse(''),
  bootsTable: zTableFilterValidator.parse(''),
  testsTable: zTableFilterValidator.parse(''),
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
  startTime?: string;
  hardware?: string[];
  treeBranch?: string;
};

export type TTestByCommitHashResponse = {
  tests: TestByCommitHash[];
};

export type PaginatedCommitHistoryByTree = {
  git_commit_hash: string;
  git_commit_name?: string;
  git_commit_tags?: string[];
  earliest_start_time: string;
  builds: RequiredStatusCount;
  boots: TableTestStatus;
  tests: TableTestStatus;
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

// TODO: These variables could be defined in the route files but it would cause
// a circular dependency, requiring rewiring of the imports.
export const treeDetailsDirectRouteName = '/_main/tree/$treeName/$branch/$hash';
export const treeDetailsRouteName = '/_main/tree/$treeId';

// This map is necessary since the "from" parameter in `useSearch` and `useParameters`
// requires the "/_main" prefix, while the "from" in `navigate` doesn't
export const treeDetailsFromMap = {
  [treeDetailsDirectRouteName]: '/tree/$treeName/$branch/$hash',
  [treeDetailsRouteName]: '/tree/$treeId',
} as const;

export type TreeDetailsRouteFrom = keyof typeof treeDetailsFromMap;

export type TreeDetailsNavigateFrom =
  (typeof treeDetailsFromMap)[TreeDetailsRouteFrom];
