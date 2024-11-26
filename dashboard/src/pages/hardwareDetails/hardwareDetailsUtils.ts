//TODO: make this utils reusable for TreeDetails and HardwareDetails

import { useSearch } from '@tanstack/react-router';

import type {
  TFilter,
  TFilterKeys,
  TFilterObjectsKeys,
  TRequestFiltersValues,
} from '@/types/hardware/hardwareDetails';

import {
  isTFilterObjectKeys,
  isTFilterNumberKeys,
} from '@/types/hardware/hardwareDetails';

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

export const useDiffFilterParams = (
  filterValue: string,
  filterSection: TFilterObjectsKeys,
): TFilter => {
  const { diffFilter: currentDiffFilter } = useSearch({
    from: '/hardware/$hardwareId/',
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

export const filterFieldMap = {
  'hardwareDetails.config_name': 'configs',
  'hardwareDetails.architecture': 'archs',
  'hardwareDetails.compiler': 'compilers',
  'hardwareDetails.valid': 'buildStatus',
  'hardwareDetails.duration_[gte]': 'buildDurationMin',
  'hardwareDetails.duration_[lte]': 'buildDurationMax',
  'hardwareDetails.trees': 'trees',
  'boot.status': 'bootStatus',
  'boot.duration_[gte]': 'bootDurationMin',
  'boot.duration_[lte]': 'bootDurationMax',
  'test.status': 'testStatus',
  'test.duration_[gte]': 'testDurationMin',
  'test.duration_[lte]': 'testDurationMax',
} as const satisfies Record<TRequestFiltersValues, TFilterKeys>;
