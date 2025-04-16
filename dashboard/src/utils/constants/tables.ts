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
