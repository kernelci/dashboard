import { useMemo } from 'react';

import {
  isTFilterNumberKeys,
  isTFilterObjectKeys,
  type TFilter,
  type TFilterObjectsKeys,
} from '@/types/general';

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
  currentDiffFilter: TFilter,
): TFilter => {
  const newFilter = useMemo(
    () => structuredClone(currentDiffFilter) || {},
    [currentDiffFilter],
  );

  if (!currentDiffFilter) {
    return {};
  }

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
