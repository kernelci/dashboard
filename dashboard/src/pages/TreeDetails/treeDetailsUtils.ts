import type { TFilter, TFilterKeys } from '@/types/tree/TreeDetails';

export const cleanFalseFilters = (diffFilter: TFilter): TFilter => {
  const cleanedFilter: TFilter = {};
  Object.entries(diffFilter).forEach(
    ([filterSectionKey, filterSectionValue]) => {
      cleanedFilter[filterSectionKey as TFilterKeys] = {};
      const currentSection = cleanedFilter[filterSectionKey as TFilterKeys];
      Object.entries(filterSectionValue).forEach(([filterKey, filterValue]) => {
        if (currentSection) {
          currentSection[filterKey] = filterValue;
        }
      });
    },
  );
  return cleanedFilter;
};
