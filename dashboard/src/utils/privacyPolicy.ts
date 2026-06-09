import { REPO_URL } from '@/utils/constants/general';

export const resolvePolicyUrl = (url: string): string => {
  if (
    url.startsWith('http://') ||
    url.startsWith('https://') ||
    url.startsWith('mailto:')
  ) {
    return url;
  }

  const [path, hash] = url.split('#');
  const base = `${REPO_URL}/blob/main/${path}`;
  return hash ? `${base}#${hash}` : base;
};
