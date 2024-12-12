const valueOrEmpty = (value: string | undefined, emptyValue = '-'): string =>
  value || emptyValue;

export const truncateBigText = (
  text: string | undefined,
  maxTextLength = 50,
): string | undefined =>
  text && text.length > maxTextLength
    ? text.slice(0, maxTextLength) + '...'
    : valueOrEmpty(text);

export const truncateUrl = (
  url: string | undefined,
  domainLength = 50,
  endPathLength = 20,
): string => {
  if (url) {
    if (url.length <= domainLength + endPathLength) {
      return url;
    }
    const protocolRegex = /^\w+:\/\//;
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
  }
  return valueOrEmpty(url);
};
