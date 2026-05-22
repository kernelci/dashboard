import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import type { TIndividualTest, TPathTests } from '@/types/general';
import { StatusTable } from '@/utils/constants/database';

import {
  type TPathTestsStatus,
  countStatus,
  createEmptyGroupStatusCounts,
  addCounts,
  getTotalTests,
} from './testStatusHelpers';

interface PrunePredicates {
  matchTest: (t: TIndividualTest) => boolean;
  matchNodePath?: (fullPath: string) => boolean;
}

export function pruneTree(
  nodes: TPathTests[],
  predicates: PrunePredicates,
): TPathTests[] {
  const results: TPathTests[] = [];

  nodes.forEach(node => {
    const fullPath = node.path_prefix
      ? `${node.path_prefix}.${node.path_group}`
      : node.path_group;

    const nodeMatchesPath = predicates.matchNodePath?.(fullPath) ?? false;

    if (nodeMatchesPath) {
      results.push(node);
      return;
    }

    const filteredSubGroups = node.sub_groups
      ? pruneTree(node.sub_groups, predicates)
      : undefined;
    const filteredIndividualTests = node.individual_tests.filter(
      predicates.matchTest,
    );

    const hasSubGroups = filteredSubGroups && filteredSubGroups.length > 0;
    const hasIndividualTests = filteredIndividualTests.length > 0;

    if (!hasSubGroups && !hasIndividualTests) {
      return;
    }

    const localGroup: TPathTestsStatus = createEmptyGroupStatusCounts();
    filteredIndividualTests.forEach(t => {
      countStatus(localGroup, t.status);
    });

    if (hasSubGroups) {
      filteredSubGroups!.forEach(g => {
        addCounts(localGroup, g);
      });
    }

    results.push({
      ...node,
      ...localGroup,
      total_tests: getTotalTests(localGroup),
      sub_groups: hasSubGroups ? filteredSubGroups : undefined,
      individual_tests: filteredIndividualTests,
      is_leaf_group: hasIndividualTests || !hasSubGroups,
    });
  });

  return results;
}

export function computeGlobalCounts(nodes: TPathTests[]): TPathTestsStatus {
  const globalGroup: TPathTestsStatus = createEmptyGroupStatusCounts();

  function walk(nodesToWalk: TPathTests[]): void {
    nodesToWalk.forEach(node => {
      node.individual_tests.forEach(t => {
        countStatus(globalGroup, t.status);
      });
      if (node.sub_groups) {
        walk(node.sub_groups);
      }
    });
  }

  walk(nodes);
  return {
    ...globalGroup,
    total_tests: getTotalTests(globalGroup),
  };
}

const PATH_SEARCH_SEPARATOR_REGEX = /[.\s_-]+/g;

export function normalizePathSearch(value: string): string {
  return value.trim().toLowerCase().replace(PATH_SEARCH_SEPARATOR_REGEX, ' ');
}

function pathMatchesSearch(candidate: string, search: string): boolean {
  const normalizedCandidate = normalizePathSearch(candidate);
  const searchTokens = normalizePathSearch(search).split(' ').filter(Boolean);

  return searchTokens.every(token => normalizedCandidate.includes(token));
}

export const matchByStatus =
  (filter: PossibleTableFilters) =>
  (t: TIndividualTest): boolean => {
    const uppercaseStatus = t.status?.toUpperCase();
    switch (filter) {
      case 'success':
        return uppercaseStatus === StatusTable.PASS;
      case 'failed':
        return uppercaseStatus === StatusTable.FAIL;
      case 'inconclusive':
        return (
          uppercaseStatus !== StatusTable.PASS &&
          uppercaseStatus !== StatusTable.FAIL
        );
      case 'all':
      default:
        return true;
    }
  };

export function matchByPathSubstring(
  path: string,
): (fullPath: string) => boolean {
  return function (fullPath: string): boolean {
    return pathMatchesSearch(fullPath, path);
  };
}

export function matchTestByPathSubstring(
  path: string,
): (test: TIndividualTest) => boolean {
  return function (test: TIndividualTest): boolean {
    return pathMatchesSearch(test.path ?? '', path);
  };
}
