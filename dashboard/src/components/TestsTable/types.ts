import type { Status } from '@/types/database';

import type { TPathTestsStatus } from './testStatusHelpers';

export type UnifiedTestRowKind = 'group' | 'leaf';

export type UnifiedTestRow = TPathTestsStatus & {
  id: string;
  kind: UnifiedTestRowKind;
  /** Path shown in the Path column (relative when grouped, full when ungrouped). */
  path: string;
  subRows?: UnifiedTestRow[];
  status?: Status;
  start_time?: string;
  duration?: string;
  hardware?: string[];
  treeBranch?: string;
  lab?: string;
};
