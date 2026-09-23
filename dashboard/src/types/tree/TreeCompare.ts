import { z } from 'zod';

import { possibleTabs } from '@/types/tree/TreeDetails';

export type CompareStatusCounts = {
  pass: number;
  fail: number;
  inconclusive: number;
};

export type CompareDelta = {
  pass: number;
  fail: number;
};

export const compareChangeTypes = [
  'regression',
  'fixed',
  'newFailure',
  'stillFailing',
  'newPass',
  'appeared',
  'disappeared',
] as const;

export type CompareChangeType = (typeof compareChangeTypes)[number];

/** Row-level classification: the backend counts no category for unchanged pairs. */
export type CompareRowChange = CompareChangeType | 'unchanged';

export type CompareChangeStats = Record<CompareChangeType, number>;

export type CompareEntitySummary = {
  sideA: CompareStatusCounts;
  sideB: CompareStatusCounts;
  delta: CompareDelta;
  changes: CompareChangeStats;
};

export type CompareRevision = {
  hash: string;
  shortHash: string;
  commitName: string;
  date: string;
  tags: string[];
};

export type TreeCompareData = {
  treeName: string;
  branch: string;
  gitUrl: string;
  summary: {
    builds: CompareEntitySummary;
    boots: CompareEntitySummary;
    tests: CompareEntitySummary;
  };
};

/** Side status for an individual compared item. */
export const compareItemStatuses = [
  'PASS',
  'FAIL',
  'INCONCLUSIVE',
  '—',
] as const;
export type CompareItemStatus = (typeof compareItemStatuses)[number];

export type CompareGroupedApiStatus = 'PASS' | 'FAIL' | 'INCONCLUSIVE';

/** Builds detail endpoint: GET .../compare/builds (bare array) */
export type TreeCompareBuildDiffApiRow = {
  config_name: string;
  architecture: string;
  compiler: string;
  status_a: CompareGroupedApiStatus | null;
  status_b: CompareGroupedApiStatus | null;
  id_a: string | null;
  id_b: string | null;
};

/** Boots/tests detail endpoints: GET .../compare/boots|tests (bare array) */
export type TreeCompareTestDiffApiRow = {
  path: string;
  config_name: string;
  architecture: string;
  platform: string;
  status_a: CompareGroupedApiStatus | null;
  status_b: CompareGroupedApiStatus | null;
  id_a: string | null;
  id_b: string | null;
};

export type CompareStatusPair = {
  from: CompareItemStatus;
  to: CompareItemStatus;
};

/** URL/storage token for an empty pair list (show all rows). */
export const compareEmptyStatusPairsToken = 'none';
/** URL token for absent (`—`) so query strings stay ASCII. */
export const compareAbsentStatusToken = 'ABSENT';
export const compareStatusPairStorageKey = 'treeCompare.statusPair';

export const compareDefaultStatusPairParams = ['PASS:FAIL', 'FAIL:PASS'];

type CompareFailureRowBase = {
  id: string;
  change: CompareRowChange;
  sideA: CompareItemStatus;
  sideB: CompareItemStatus;
  idA: string | null;
  idB: string | null;
};

export type CompareBuildFailureRow = CompareFailureRowBase & {
  config: string;
  arch: string;
  compiler: string;
};

export type CompareBootFailureRow = CompareFailureRowBase & {
  path: string;
  config: string;
  arch: string;
  hardware: string;
};

export type CompareTestFailureRow = CompareFailureRowBase & {
  path: string;
  config: string;
  arch: string;
  hardware: string;
};

export type CompareFailureRow =
  | CompareBuildFailureRow
  | CompareBootFailureRow
  | CompareTestFailureRow;

export const compareDefaultValues = {
  hashA: '',
  hashB: '',
  origin: 'maestro',
  currentPageTab: 'global.builds' as const,
};

export const compareSearchSchema = z.object({
  hashA: z.string().catch(''),
  hashB: z.string().catch(''),
  origin: z
    .string()
    .default(compareDefaultValues.origin)
    .catch(compareDefaultValues.origin),
  currentPageTab: z
    .enum(possibleTabs)
    .default(compareDefaultValues.currentPageTab)
    .catch(compareDefaultValues.currentPageTab),
  // Omit = unspecified (hydrate from localStorage, then hardcoded default).
  // `none` is an explicit empty list.
  statusPair: z.preprocess(value => {
    if (value === undefined) {
      return undefined;
    }
    if (value === '') {
      return [compareEmptyStatusPairsToken];
    }
    return Array.isArray(value) ? value : [value];
  }, z.array(z.string()).optional().catch(undefined)),
});

export type CompareSearch = z.infer<typeof compareSearchSchema>;

export const compareRouteName = '/_main/tree/$treeName/$branch/compare';
export const compareNavigateFrom = '/tree/$treeName/$branch/compare';
