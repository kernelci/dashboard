export const valueOrEmpty = (
  value: string | undefined,
  emptyValue = '-',
): string => value || emptyValue;

export const shouldTruncate = (value: string, maxLength = 50): boolean =>
  value.length > maxLength;

export const truncateBigText = (
  text: string | undefined,
  maxTextLength = 50,
): string => {
  if (!text) {
    return valueOrEmpty(text);
  }
  if (!shouldTruncate(text, maxTextLength)) {
    return text;
  }
  return text.slice(0, maxTextLength) + '...';
};

const protocolRegex = /^\w+:\/\//;

export const isUrl = (possibleUrl: string): boolean => {
  return protocolRegex.test(possibleUrl);
};

export const truncateUrl = (
  url: string | undefined,
  domainLength = 50,
  endPathLength = 20,
): string => {
  if (!url) {
    return valueOrEmpty(url);
  }
  if (!shouldTruncate(url, domainLength + endPathLength)) {
    return url;
  }

  try {
    const urlObject = new URL(url);

    const domain = urlObject.hostname.slice(0, domainLength);
    const lastPath = urlObject.pathname.slice(-endPathLength);
    return `${domain}...${lastPath}`;
  } catch {
    console.error('Non URL passing to truncateUrl', url);
    return url;
  }
};

export const matchesRegexOrIncludes = (
  text: string | undefined | null,
  pattern: string,
): boolean => {
  if (!text) {
    return false;
  }
  try {
    const regex = new RegExp(pattern, 'i');
    return regex.test(text);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    return text.includes(pattern);
  }
};

export const includesInAnStringOrStringArray = (
  searched: string | string[],
  inputFilter: string,
): boolean => {
  if (Array.isArray(searched)) {
    return searched.some(element =>
      matchesRegexOrIncludes(element, inputFilter),
    );
  }
  return matchesRegexOrIncludes(searched, inputFilter);
};
