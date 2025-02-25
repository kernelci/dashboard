export const getTestHardware = ({
  misc,
  compatibles,
  defaultValue,
}: {
  misc?: Record<string, unknown>;
  compatibles?: string[];
  defaultValue?: string;
}): string => {
  const platform = misc?.['platform'];
  if (typeof platform === 'string' && platform !== '') {
    return platform;
  }

  if (compatibles && compatibles.length > 0) {
    return compatibles[0];
  }

  return defaultValue ?? '-';
};
