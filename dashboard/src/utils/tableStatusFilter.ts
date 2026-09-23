export const tableStatusOptions = [
  'success',
  'failed',
  'inconclusive',
] as const;

export type TableStatusOption = (typeof tableStatusOptions)[number];

export type TableStatusSelection = TableStatusOption[];

export const defaultTableStatusSelection = [...tableStatusOptions];

const isTableStatusOption = (item: unknown): item is TableStatusOption =>
  typeof item === 'string' &&
  (tableStatusOptions as readonly string[]).includes(item);

export const normalizeTableStatusSelection = (
  value: unknown,
): TableStatusSelection => {
  if (Array.isArray(value)) {
    const valid = value.filter(isTableStatusOption);
    if (valid.length === 0 && value.length > 0) {
      return defaultTableStatusSelection;
    }
    return valid;
  }

  if (isTableStatusOption(value)) {
    return [value];
  }

  return defaultTableStatusSelection;
};

export const toggleTableStatus = (
  selection: TableStatusSelection | undefined,
  option: TableStatusOption,
): TableStatusSelection => {
  const active = selection ?? defaultTableStatusSelection;
  if (active.includes(option)) {
    return active.filter(item => item !== option);
  }
  return [...active, option].sort(
    (a, b) => tableStatusOptions.indexOf(a) - tableStatusOptions.indexOf(b),
  );
};
