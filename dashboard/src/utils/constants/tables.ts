export type TableKeys =
  | 'treeListing'
  | 'treeDetailsBuilds'
  | 'treeDetailsBoots'
  | 'treeDetailsTests'
  | 'hardwareListing'
  | 'hardwareDetailsBuilds'
  | 'hardwareDetailsBoots'
  | 'hardwareDetailsTests'
  | 'hardwareDetailsTrees'
  | 'buildDetailsTests'
  | 'issueDetailsTests'
  | 'issueDetailsBuilds'
  | 'issueListing';

// Regexes to define pinned trees with "tree_name/git_repository_branch"
export const PinnedTrees: RegExp[] = [
  /^mainline\/master/,
  /^next\/master/,
  /^stable\/.*/,
] as const;

/** Default column layout bounds (px); overridable via column meta or normalizeColumns defaults. */
export const DEFAULT_COLUMN_MIN_WIDTH = 80;
export const DEFAULT_COLUMN_MAX_WIDTH = 320;
export const DEFAULT_COLUMN_WIDTH_WEIGHT = 1;

/**
 * Min widths for grouped status columns (3 ColoredCircles + gaps + cell padding).
 * Sized so PASS/FAIL/Inconclusive can show the given digit counts without clipping.
 */
export const BUILD_STATUS_MIN_WIDTH = 168; // 3 digits each
export const BOOT_STATUS_MIN_WIDTH = 196; // 4 digits each
export const TEST_STATUS_MIN_WIDTH = 224; // 5 digits each

/** Horizontal border width on the table frame (border-x, 1px each side). */
export const TABLE_FRAME_BORDER_X = 2;
