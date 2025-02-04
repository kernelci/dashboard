import { sanitizeTableValue } from '@/components/Table/tableUtils';

import type { TestHistory } from '@/types/general';

export const buildHardwareArray = (
  environment_compatible?: TestHistory['environment_compatible'],
  environment_misc?: TestHistory['environment_misc'],
): string[] | undefined => {
  const miscArray: string[] = environment_misc?.platform
    ? [environment_misc.platform]
    : [];
  const envArray: string[] = environment_compatible ?? [];
  return miscArray.concat(envArray);
};

export const buildTreeBranch = (
  treeName?: string,
  gitRepositoryBranch?: string,
): string => {
  return `${sanitizeTableValue(treeName)} / ${sanitizeTableValue(gitRepositoryBranch)}`;
};
