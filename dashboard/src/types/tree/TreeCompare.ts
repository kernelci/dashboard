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

export type CompareEntitySummary = {
  sideA: CompareStatusCounts;
  sideB: CompareStatusCounts;
  delta: CompareDelta;
};

export type CompareGroupRow = {
  id: string;
  label: string;
  sideA: CompareStatusCounts;
  sideB: CompareStatusCounts;
  delta: CompareDelta;
};

export type CompareRevision = {
  hash: string;
  shortHash: string;
  commitName: string;
  date: string;
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
  groups: {
    builds: CompareGroupRow[];
    boots: CompareGroupRow[];
    tests: CompareGroupRow[];
  };
};

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
});

export type CompareSearch = z.infer<typeof compareSearchSchema>;

export const compareRouteName = '/_main/tree/$treeName/$branch/compare';
export const compareNavigateFrom = '/tree/$treeName/$branch/compare';
