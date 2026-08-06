import type { TIndividualTest, TPathTests } from '@/types/general';

import {
  type TPathTestsStatus,
  createEmptyGroupStatusCounts,
  countStatus,
  getTotalTests,
} from './testStatusHelpers';
import { buildGroupSummaries } from './groupSummaries';
import type { UnifiedTestRow } from './types';

function statusCountsFromTest(test: TIndividualTest): TPathTestsStatus {
  const counts = createEmptyGroupStatusCounts();
  countStatus(counts, test.status);
  return { ...counts, total_tests: getTotalTests(counts) };
}

function testToLeafRow(test: TIndividualTest): UnifiedTestRow {
  return {
    id: test.id,
    kind: 'leaf',
    path: test.path ?? '',
    ...statusCountsFromTest(test),
    status: test.status,
    start_time: test.start_time,
    duration: test.duration,
    hardware: test.hardware,
    treeBranch: test.treeBranch,
    lab: test.lab,
  };
}

function toGroupRow(
  node: TPathTests,
  children: UnifiedTestRow[],
): UnifiedTestRow {
  const fullPath = node.path_prefix
    ? `${node.path_prefix}.${node.path_group}`
    : node.path_group;
  return {
    id: `group:${fullPath}`,
    kind: 'group',
    path: node.path_group,
    done_tests: node.done_tests,
    error_tests: node.error_tests,
    fail_tests: node.fail_tests,
    miss_tests: node.miss_tests,
    pass_tests: node.pass_tests,
    skip_tests: node.skip_tests,
    null_tests: node.null_tests,
    total_tests: node.total_tests,
    subRows: children,
    summaries: buildGroupSummaries(children),
  };
}

/**
 * Converts a collapsed path tree into unified group/leaf rows.
 *
 * Groups wrapping a single item are omitted: a node with one leaf child
 * (after recursion) is hoisted to the parent.
 */
export function buildUnifiedTestsTree(nodes: TPathTests[]): UnifiedTestRow[] {
  const rows: UnifiedTestRow[] = [];

  nodes.forEach(node => {
    const subGroupRows = node.sub_groups
      ? buildUnifiedTestsTree(node.sub_groups)
      : [];

    const directLeafRows = node.individual_tests.map(testToLeafRow);

    const children = [...subGroupRows, ...directLeafRows];

    if (children.length === 0) {
      return;
    }

    if (children.length === 1 && children[0].kind === 'leaf') {
      rows.push(children[0]);
      return;
    }

    rows.push(toGroupRow(node, children));
  });

  return rows;
}

/** Flat leaf list with full paths — used when grouping is disabled. */
export function flattenTestsToLeafRows(nodes: TPathTests[]): UnifiedTestRow[] {
  const rows: UnifiedTestRow[] = [];

  const walk = (nodesToWalk: TPathTests[]): void => {
    nodesToWalk.forEach(node => {
      node.individual_tests.forEach(test => {
        rows.push(testToLeafRow(test));
      });
      if (node.sub_groups) {
        walk(node.sub_groups);
      }
    });
  };

  walk(nodes);
  return rows;
}
