import { useSearch } from '@tanstack/react-router';

import type {
  TFilter,
  TFilterKeys,
  TFilterObjectsKeys,
} from '@/types/tree/TreeDetails';

import {
  isTFilterObjectKeys,
  isTFilterNumberKeys,
} from '@/types/tree/TreeDetails';
import type { TRequestFiltersValues } from '@/utils/filters';

export const cleanFalseFilters = (diffFilter: TFilter): TFilter => {
  const cleanedFilter: TFilter = {};
  Object.entries(diffFilter).forEach(
    ([filterSectionKey, filterSectionValue]) => {
      if (isTFilterObjectKeys(filterSectionKey)) {
        cleanedFilter[filterSectionKey] = {};
        const currentSection = cleanedFilter[filterSectionKey];
        Object.entries(filterSectionValue).forEach(
          ([filterKey, filterValue]) => {
            if (currentSection) {
              currentSection[filterKey] = filterValue;
            }
          },
        );
      } else if (
        isTFilterNumberKeys(filterSectionKey) &&
        typeof filterSectionValue === 'number'
      ) {
        cleanedFilter[filterSectionKey] = filterSectionValue;
      }
    },
  );

  return cleanedFilter;
};

export const filterFieldMap = {
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
} as const satisfies Record<TRequestFiltersValues, TFilterKeys>;

export const useDiffFilterParams = (
  filterValue: string,
  filterSection: TFilterObjectsKeys,
): TFilter => {
  const { diffFilter: currentDiffFilter } = useSearch({
    from: '/tree/$treeId/',
  });

  if (!currentDiffFilter) return {};

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
