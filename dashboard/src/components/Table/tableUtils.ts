const MAX_NUMBER_CHAR = 12;

const truncateTableValue = (value: string): string =>
  value.substring(0, MAX_NUMBER_CHAR) +
  (value.length > MAX_NUMBER_CHAR ? '...' : '');

export const sanitizeTableValue = (value: string, truncate = true): string =>
  (truncate ? truncateTableValue(value) : value) || '-';
