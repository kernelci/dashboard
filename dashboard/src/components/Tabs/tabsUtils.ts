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
  if (!currentDiffFilter) return {} as TFilter;

  const newFilter = (structuredClone(currentDiffFilter) || {}) as TFilter;
  // This seems redundant but we do this to keep the pointer to newFilter[filterSection]
  newFilter[filterSection] = newFilter[filterSection] ?? {};

  const configs = newFilter[filterSection] as Record<string, boolean>;
  if (configs[filterValue]) {
    delete configs[filterValue];
  } else {
    configs[filterValue] = true;
  }

  return newFilter;
};
