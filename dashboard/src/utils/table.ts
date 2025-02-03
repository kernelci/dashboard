import { sanitizeTableValue } from '@/components/Table/tableUtils';

import type { TestHistory } from '@/types/general';

export const buildHardwareArray = (
  environment_compatible?: TestHistory['environment_compatible'],
  misc?: TestHistory['misc'],
): string[] | undefined => {
  const miscArray: string[] = misc?.platform ? [misc.platform] : [];
  const envArray: string[] = environment_compatible ?? [];
  return miscArray.concat(envArray);
};

export const buildTreeBranch = (
  treeName?: string,
  gitRepositoryBranch?: string,
): string => {
  return `${sanitizeTableValue(treeName)} / ${sanitizeTableValue(gitRepositoryBranch)}`;
};
