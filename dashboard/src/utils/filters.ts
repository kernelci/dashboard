import { useSearch } from '@tanstack/react-router';

import {
  TFilter,
  TFilterObjectsKeys,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';

// TODO: We can improve this idea and replace mapFilterToReq entirely
const requestFilters = {
  test: [
    'test.status',
    'test.duration_[gte]',
    'test.duration_[lte]',
    'boot.status',
    'boot.duration_[gte]',
    'boot.duration_[lte]',
  ],
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
    if (target == 'test') {
      acc[k] = v;
    } else {
      acc[field] = v;
    }
  });

  return acc;
};

export const useDiffFilterParams = (
  filterValue: string,
  filterSection: TFilterObjectsKeys,
): TFilter => {
  const { diffFilter: currentDiffFilter } = useSearch({
    from: '/tree/$treeId',
  });

  const newFilter = structuredClone(currentDiffFilter) || {};
  // This seems redundant but we do this to keep the pointer to newFilter[filterSection]
  newFilter[filterSection] = newFilter[filterSection] ?? {};

  const configs = newFilter[filterSection];
  if (configs[filterValue]) {
    delete configs[filterValue];
  } else {
    configs[filterValue] = true;
  }

  return newFilter;
};
