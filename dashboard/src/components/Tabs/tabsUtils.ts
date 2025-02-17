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

export const generateDiffFilter = (
  filterValue: string,
  filterSectionKey: TFilterObjectsKeys,
  currentDiffFilter: TFilter,
): TFilter => {
  const newFilter = structuredClone(currentDiffFilter) || {};

  const filterSectionData = newFilter[filterSectionKey] ?? {};
  if (filterSectionData[filterValue]) {
    delete filterSectionData[filterValue];
  } else {
    filterSectionData[filterValue] = true;
  }

  return {
    ...newFilter,
    [filterSectionKey]: filterSectionData,
  };
};
