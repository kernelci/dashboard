import type { TPathTests } from '@/types/general';

/**
 * Recursively collapses single-child chains in the test tree.
 *
 * A node N is merged with its sole child C when:
 * - N has exactly one sub_group, AND
 * - N has no individual_tests
 *
 * The merge creates a new node with:
 * - path_group = `${N.path_group}.${C.path_group}`
 * - path_prefix = N.path_prefix (unchanged)
 * - All other properties from C (counts, sub_groups, individual_tests, is_leaf_group)
 */
export function collapseSingleChildChains(nodes: TPathTests[]): TPathTests[] {
  return nodes.map(node => collapseNode(node));
}

function collapseNode(node: TPathTests): TPathTests {
  const collapsedSubGroups = node.sub_groups
    ? node.sub_groups.map(child => collapseNode(child))
    : undefined;

  let current: TPathTests = {
    ...node,
    sub_groups: collapsedSubGroups,
  };

  while (
    current.sub_groups &&
    current.sub_groups.length === 1 &&
    current.individual_tests.length === 0
  ) {
    const child = current.sub_groups[0];

    current = {
      ...child,
      path_group: `${current.path_group}.${child.path_group}`,
      path_prefix: current.path_prefix,
    };
  }

  return current;
}
