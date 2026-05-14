import type {
  HardwareRevisionSelection,
  HardwareSelectorBranch,
  HardwareSelectorRevision,
  HardwareSelectorTree,
} from '@/types/hardware';

type ResolvedHardwareSelection = {
  selection: HardwareRevisionSelection | null;
  revisionStartTime: string | null;
};

export type HardwareRevisionSelectorValue = {
  tree: string;
  branch: string;
  revision: string;
};

const BRANCH_VALUE_SEPARATOR = '::';

const getFirstBranch = (
  branches: HardwareSelectorBranch[],
): HardwareSelectorBranch | null => {
  return branches[0] ?? null;
};

const getFirstRevision = (
  revisions: HardwareSelectorRevision[],
): HardwareSelectorRevision | null => {
  return revisions[0] ?? null;
};

const matchesCommitToken = (
  hash: string,
  name: string | null | undefined,
  token: string,
): boolean => {
  const normalizedToken = token.toLowerCase();
  return (
    hash.toLowerCase() === normalizedToken ||
    (name?.toLowerCase().includes(normalizedToken) ?? false)
  );
};

export const encodeBranchValue = (
  gitRepositoryUrl: string,
  gitBranch: string,
): string => {
  return `${encodeURIComponent(gitRepositoryUrl)}${BRANCH_VALUE_SEPARATOR}${encodeURIComponent(gitBranch)}`;
};

export const decodeBranchValue = (
  branchValue: string,
): { gitRepositoryUrl: string; gitBranch: string } | null => {
  const [encodedGitRepositoryUrl, encodedGitBranch] = branchValue.split(
    BRANCH_VALUE_SEPARATOR,
  );

  if (!encodedGitRepositoryUrl || !encodedGitBranch) {
    return null;
  }

  return {
    gitRepositoryUrl: decodeURIComponent(encodedGitRepositoryUrl),
    gitBranch: decodeURIComponent(encodedGitBranch),
  };
};

const getGlobalFirstHardwareSelection = (
  trees: HardwareSelectorTree[],
): {
  selection: HardwareRevisionSelection;
  revisionStartTime: string;
} | null => {
  for (const tree of trees) {
    const firstBranch = getFirstBranch(tree.branches);
    if (firstBranch === null) {
      continue;
    }

    const firstRevision = getFirstRevision(firstBranch.revisions);
    if (firstRevision === null) {
      continue;
    }

    return {
      selection: {
        treeName: tree.tree_name,
        gitRepositoryUrl: firstBranch.git_repository_url,
        gitBranch: firstBranch.git_repository_branch,
        gitCommitHash: firstRevision.git_commit_hash,
      },
      revisionStartTime: firstRevision.start_time,
    };
  }

  return null;
};

export const findSelectionByCommitTokens = (
  trees: HardwareSelectorTree[],
  tokens: string[],
): {
  selection: HardwareRevisionSelection;
  revisionStartTime: string;
} | null => {
  if (tokens.length === 0) {
    return null;
  }

  for (const tree of trees) {
    for (const branch of tree.branches) {
      for (const revision of branch.revisions) {
        if (
          tokens.some(token =>
            matchesCommitToken(
              revision.git_commit_hash,
              revision.git_commit_name,
              token,
            ),
          )
        ) {
          return {
            selection: {
              treeName: tree.tree_name,
              gitRepositoryUrl: branch.git_repository_url,
              gitBranch: branch.git_repository_branch,
              gitCommitHash: revision.git_commit_hash,
            },
            revisionStartTime: revision.start_time,
          };
        }
      }
    }
  }

  return null;
};

export const getTreeBySelection = (
  trees: HardwareSelectorTree[],
  treeName: string,
): HardwareSelectorTree | null => {
  return trees.find(tree => tree.tree_name === treeName) ?? null;
};

export const getBranchBySelection = (
  tree: HardwareSelectorTree,
  gitRepositoryUrl: string,
  gitBranch: string,
): HardwareSelectorBranch | null => {
  return (
    tree.branches.find(branch => {
      return (
        branch.git_repository_url === gitRepositoryUrl &&
        branch.git_repository_branch === gitBranch
      );
    }) ?? null
  );
};

export const getRevisionBySelection = (
  branch: HardwareSelectorBranch,
  gitCommitHash: string,
): HardwareSelectorRevision | null => {
  return (
    branch.revisions.find(
      revision => revision.git_commit_hash === gitCommitHash,
    ) ?? null
  );
};

export const resolveHardwareSelection = ({
  trees,
  selectionFromUrl,
  hasSelectionParams,
  intentCommits,
}: {
  trees: HardwareSelectorTree[];
  selectionFromUrl: HardwareRevisionSelection | null;
  hasSelectionParams: boolean;
  intentCommits?: string[];
}): ResolvedHardwareSelection => {
  if (trees.length === 0) {
    return {
      selection: null,
      revisionStartTime: null,
    };
  }

  if (!hasSelectionParams && intentCommits?.length) {
    const selectionFromIntent = findSelectionByCommitTokens(
      trees,
      intentCommits,
    );
    if (selectionFromIntent !== null) {
      return {
        selection: selectionFromIntent.selection,
        revisionStartTime: selectionFromIntent.revisionStartTime,
      };
    }
  }

  if (selectionFromUrl !== null) {
    const selectedTree = getTreeBySelection(trees, selectionFromUrl.treeName);
    if (selectedTree !== null) {
      const selectedBranch = getBranchBySelection(
        selectedTree,
        selectionFromUrl.gitRepositoryUrl,
        selectionFromUrl.gitBranch,
      );

      if (selectedBranch !== null) {
        const selectedRevision = getRevisionBySelection(
          selectedBranch,
          selectionFromUrl.gitCommitHash,
        );

        if (selectedRevision !== null) {
          return {
            selection: selectionFromUrl,
            revisionStartTime: selectedRevision.start_time,
          };
        }
      }
    }
  }

  const globalSelection = getGlobalFirstHardwareSelection(trees);
  if (globalSelection === null) {
    return {
      selection: null,
      revisionStartTime: null,
    };
  }

  return {
    selection: globalSelection.selection,
    revisionStartTime: globalSelection.revisionStartTime,
  };
};

export const getSelectionForTreeChange = ({
  trees,
  treeName,
}: {
  trees: HardwareSelectorTree[];
  treeName: string;
}): HardwareRevisionSelection | null => {
  const selectedTree = getTreeBySelection(trees, treeName);
  if (selectedTree === null) {
    return null;
  }

  const selectedBranch = getFirstBranch(selectedTree.branches);
  if (selectedBranch === null) {
    return null;
  }

  const selectedRevision = getFirstRevision(selectedBranch.revisions);
  if (selectedRevision === null) {
    return null;
  }

  return {
    treeName: selectedTree.tree_name,
    gitRepositoryUrl: selectedBranch.git_repository_url,
    gitBranch: selectedBranch.git_repository_branch,
    gitCommitHash: selectedRevision.git_commit_hash,
  };
};

export const getSelectionForBranchChange = ({
  tree,
  gitRepositoryUrl,
  gitBranch,
}: {
  tree: HardwareSelectorTree;
  gitRepositoryUrl: string;
  gitBranch: string;
}): HardwareRevisionSelection | null => {
  const selectedBranch = getBranchBySelection(
    tree,
    gitRepositoryUrl,
    gitBranch,
  );
  if (selectedBranch === null) {
    return null;
  }

  const selectedRevision = getFirstRevision(selectedBranch.revisions);
  if (selectedRevision === null) {
    return null;
  }

  return {
    treeName: tree.tree_name,
    gitRepositoryUrl: selectedBranch.git_repository_url,
    gitBranch: selectedBranch.git_repository_branch,
    gitCommitHash: selectedRevision.git_commit_hash,
  };
};
