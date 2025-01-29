import type { TestHistory } from '@/types/general';

export const buildHardwareArray = (
  environment_compatible?: TestHistory['environment_compatible'],
  misc?: TestHistory['misc'],
): string[] | undefined => {
  return environment_compatible
    ? environment_compatible
    : misc?.platform
      ? [misc?.platform]
      : undefined;
};
