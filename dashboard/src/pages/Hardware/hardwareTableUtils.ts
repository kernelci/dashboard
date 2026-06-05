import type { TFilter } from '@/types/general';
import type { PossibleTabs } from '@/types/tree/TreeDetails';

type ListingSearch = Record<string, unknown>;

export const buildHardwareDetailsSearch = ({
  previousSearch,
  currentPageTab,
  startTimestampInSeconds,
  endTimestampInSeconds,
  newDiffFilter,
}: {
  previousSearch: ListingSearch;
  currentPageTab: PossibleTabs;
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  newDiffFilter?: TFilter;
}): ListingSearch => {
  const {
    treeIndexes: _treeIndexes,
    treeCommits: _treeCommits,
    treeName: _treeName,
    gitRepositoryUrl: _gitRepositoryUrl,
    gitBranch: _gitBranch,
    gitCommitHash: _gitCommitHash,
    ...searchWithoutTreeParams
  } = previousSearch;

  const previousDiffFilter =
    (searchWithoutTreeParams.diffFilter as Record<string, unknown>) ?? {};

  return {
    ...searchWithoutTreeParams,
    currentPageTab,
    startTimestampInSeconds,
    endTimestampInSeconds,
    diffFilter: { ...previousDiffFilter, ...newDiffFilter },
  };
};
