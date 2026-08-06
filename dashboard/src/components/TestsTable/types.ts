import type { Status } from '@/types/database';

import type { TPathTestsStatus } from './testStatusHelpers';

export type UnifiedTestRowKind = 'group' | 'leaf';

/** Aggregated value for a leaf-backed column on a group row. */
export type GroupFieldSummary =
  | { kind: 'uniform'; value: unknown }
  | { kind: 'mixed'; count: number }
  | { kind: 'dateRange'; min: string; max: string };

export type UnifiedTestRow = TPathTestsStatus & {
  id: string;
  kind: UnifiedTestRowKind;
  /** Path shown in the Path column (relative when grouped, full when ungrouped). */
  path: string;
  subRows?: UnifiedTestRow[];
  /** Present on group rows for non-path/status leaf columns. */
  summaries?: Partial<Record<string, GroupFieldSummary>>;
  status?: Status;
  start_time?: string;
  duration?: string;
  hardware?: string[];
  treeBranch?: string;
  lab?: string;
};
