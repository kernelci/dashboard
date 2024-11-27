import { useMemo } from 'react';

export type RecordDiffBooleanType = Record<string, Record<string, boolean>>;
export type RecordDiffNumberType = Record<string, number>;

export type RecordDiffType = RecordDiffNumberType | RecordDiffBooleanType;

export const useDiffFilterParams = <
  TFilterObjectsKeys extends string,
  TFilter extends Record<TFilterObjectsKeys, Record<string, boolean>>,
>(
  filterValue: string,
  filterSection: TFilterObjectsKeys,
  currentDiffFilter: TFilter,
): TFilter => {
  const newFilter = useMemo(
    () => structuredClone(currentDiffFilter) || {},
    [currentDiffFilter],
  );

  if (!currentDiffFilter) return {};

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
