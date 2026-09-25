import type { TestHistory, TPathTests } from '@/types/general';
import { buildHardwareArray, buildTreeBranch } from '@/utils/table';
import { EMPTY_VALUE } from '@/lib/string';

import {
  type GroupNode,
  type TPathTestsStatus,
  countStatus,
  createEmptyNode,
  addCounts,
  getTotalTests,
} from './testStatusHelpers';

export function buildTestsTree(
  testHistory: TestHistory[] | undefined,
): TPathTests[] {
  const rootGroups = new Map<string, GroupNode>();

  if (testHistory !== undefined) {
    testHistory.forEach(e => {
      const path = e.path || EMPTY_VALUE;
      const segments = path === EMPTY_VALUE ? [EMPTY_VALUE] : path.split('.');

      let currentLevel = rootGroups;

      segments.forEach((segment, index) => {
        const isLastSegment = index === segments.length - 1;

        if (!currentLevel.has(segment)) {
          currentLevel.set(segment, createEmptyNode());
        }

        const node = currentLevel.get(segment)!;

        if (isLastSegment) {
          countStatus(node, e.status);
          node.individual_tests.push({
            id: e.id,
            duration: e.duration?.toString() ?? '',
            path,
            start_time: e.start_time,
            status: e.status,
            hardware: buildHardwareArray(
              e.environment_compatible,
              e.environment_misc,
            ),
            treeBranch: buildTreeBranch(e.tree_name, e.git_repository_branch),
            lab: e.lab,
            config: e.config,
            arch: e.arch,
            platform: e.platform,
            sideA: e.sideA,
            sideB: e.sideB,
            change: e.change,
          });
        } else {
          currentLevel = node.children;
        }
      });
    });
  }

  return toTPathTests(rootGroups, '');
}

function toTPathTests(
  groups: Map<string, GroupNode>,
  parentPath: string,
): TPathTests[] {
  const result: TPathTests[] = [];

  groups.forEach((node, segment) => {
    const fullPath = parentPath === '' ? segment : `${parentPath}.${segment}`;

    const subGroups =
      node.children.size > 0 ? toTPathTests(node.children, fullPath) : [];

    const aggregatedCounts: TPathTestsStatus = {
      done_tests: node.done_tests,
      error_tests: node.error_tests,
      fail_tests: node.fail_tests,
      miss_tests: node.miss_tests,
      pass_tests: node.pass_tests,
      skip_tests: node.skip_tests,
      null_tests: node.null_tests,
      total_tests: 0,
    };

    subGroups.forEach(child => {
      addCounts(aggregatedCounts, child);
    });

    const hasDirectTests = node.individual_tests.length > 0;

    result.push({
      done_tests: aggregatedCounts.done_tests,
      error_tests: aggregatedCounts.error_tests,
      fail_tests: aggregatedCounts.fail_tests,
      miss_tests: aggregatedCounts.miss_tests,
      pass_tests: aggregatedCounts.pass_tests,
      null_tests: aggregatedCounts.null_tests,
      skip_tests: aggregatedCounts.skip_tests,
      total_tests: getTotalTests(aggregatedCounts),
      path_group: segment,
      path_prefix: parentPath,
      individual_tests: node.individual_tests,
      sub_groups: subGroups.length > 0 ? subGroups : undefined,
      is_leaf_group: hasDirectTests || subGroups.length === 0,
    });
  });

  return result;
}
