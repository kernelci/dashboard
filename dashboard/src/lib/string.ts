const valueOrEmpty = (value: string | undefined, emptyValue = '-'): string =>
  value || emptyValue;

export const truncateBigText = (
  text: string | undefined,
  maxTextLength = 50,
): string | undefined =>
  text && text.length > maxTextLength
    ? text.slice(0, maxTextLength) + '...'
    : valueOrEmpty(text);
