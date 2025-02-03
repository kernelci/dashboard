import { sanitizeTableValue } from '@/components/Table/tableUtils';

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

export const buildTreeBranch = (
  treeName?: string,
  gitRepositoryBranch?: string,
): string => {
  return `${sanitizeTableValue(treeName)} / ${sanitizeTableValue(gitRepositoryBranch)}`;
};
