import { TTreeDetailsFilter } from '@/types/tree/TreeDetails';

// TODO: We can improve this idea and replace mapFilterToReq entirely
const requestFilters = {
  boot: ['boot.status'],
  test: ['test.status'],
  treeDetails: [
    'treeDetails.config_name',
    'treeDetails.architecture',
    'treeDetails.compiler',
    'treeDetails.valid',
    'treeDetails.duration_[gte]',
    'treeDetails.duration_[lte]',
  ],
} as const;

type TRequestFiltersKey = keyof typeof requestFilters;
export type TRequestFiltersValues =
  (typeof requestFilters)[TRequestFiltersKey][number];

export const getTargetFilter = (
  filter: TTreeDetailsFilter,
  target: TRequestFiltersKey,
): TTreeDetailsFilter => {
  const targetFilter: readonly string[] = requestFilters[target];
  const acc: Record<string, unknown> = {}; //fix this

  Object.entries(filter).forEach(([k, v]) => {
    if (!targetFilter.includes(k)) return;

    const splitted = k.split('.');
    const field = splitted[splitted.length - 1];
    acc[field] = v;
  });

  return acc;
};
