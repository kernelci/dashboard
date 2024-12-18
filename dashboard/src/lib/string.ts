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
  const searchParamsRegex = /\?.*$/;
  const replacedUrl = url
    .replace(protocolRegex, '')
    .replace(searchParamsRegex, '');
  const splittedUrl = replacedUrl.split('/');
  const hostname = splittedUrl[0];
  const pathname = splittedUrl?.pop();
  const domain = hostname ? hostname.slice(0, domainLength) : '';
  const lastPath = pathname ? pathname.slice(-endPathLength) : '';
  return `${domain}...${lastPath}`;
};
