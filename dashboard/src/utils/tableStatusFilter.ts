export const tableStatusOptions = [
  'success',
  'failed',
  'inconclusive',
] as const;

export type TableStatusOption = (typeof tableStatusOptions)[number];

export const possibleTableFilters = ['all', ...tableStatusOptions] as const;

export type TableStatusToggleValue = (typeof possibleTableFilters)[number];

export type TableStatusSelection = TableStatusOption[];

export const defaultTableStatusSelection = [...tableStatusOptions];

export const isFullTableStatusSelection = (
  selection: TableStatusSelection,
): boolean => tableStatusOptions.every(option => selection.includes(option));

export const normalizeTableStatusSelection = (
  value: unknown,
): TableStatusSelection => {
  if (Array.isArray(value)) {
    return value.filter(
      (item): item is TableStatusOption =>
        typeof item === 'string' &&
        (tableStatusOptions as readonly string[]).includes(item),
    );
  }

  if (
    value === 'all' ||
    value === '' ||
    value === null ||
    value === undefined
  ) {
    return defaultTableStatusSelection;
  }

  if (value === 'success' || value === 'failed' || value === 'inconclusive') {
    return [value];
  }

  return defaultTableStatusSelection;
};

export const toggleTableStatus = (
  selection: TableStatusSelection | undefined,
  option: TableStatusToggleValue,
): TableStatusSelection => {
  const active = selection ?? defaultTableStatusSelection;
  if (option === 'all') {
    return isFullTableStatusSelection(active)
      ? []
      : [...defaultTableStatusSelection];
  }
  if (active.includes(option)) {
    return active.filter(item => item !== option);
  }
  return [...active, option].sort(
    (a, b) => tableStatusOptions.indexOf(a) - tableStatusOptions.indexOf(b),
  );
};

export const tableStatusFilterValueForColumn = (
  selection: TableStatusSelection,
): TableStatusSelection | undefined =>
  isFullTableStatusSelection(selection) ? undefined : selection;
