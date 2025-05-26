import { isTFilterNumberKeys, isTFilterObjectKeys } from '@/types/general';
import type { TFilterKeys, TFilter, TFilterObjectsKeys } from '@/types/general';
import { CULPRIT_CODE, HAS_INCIDENT_OPTION } from '@/utils/constants/issues';

/**
 * Stores filter values which are true by default.
 *
 * This is used to avoid removing false filters for those keys,
 * since "false" is the option that the user will want to use
 */
const defaultTrueFilters: Partial<Record<TFilterKeys, string>> = {
  issueCulprits: CULPRIT_CODE,
  issueOptions: HAS_INCIDENT_OPTION,
};

const defaultTrueFilterValues = Object.values(defaultTrueFilters);

export const cleanFalseFilters = (diffFilter: TFilter): TFilter => {
  const cleanedFilter: TFilter = {};
  Object.entries(diffFilter).forEach(
    ([filterSectionKey, filterSectionValue]) => {
      if (isTFilterObjectKeys(filterSectionKey)) {
        cleanedFilter[filterSectionKey] = {};
        const currentSection = cleanedFilter[filterSectionKey];
        Object.entries(filterSectionValue as Record<string, boolean>).forEach(
          ([filterKey, filterValue]) => {
            if (
              currentSection &&
              (filterValue || defaultTrueFilterValues.includes(filterKey))
            ) {
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
