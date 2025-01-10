interface TreeIdentifierParams {
  treeName: string;
  gitRepositoryUrl: string;
  gitRepositoryBranch: string;
}

export const makeTreeIdentifierKey = ({
  treeName,
  gitRepositoryUrl,
  gitRepositoryBranch,
}: TreeIdentifierParams): string => {
  return `${treeName}-${gitRepositoryUrl}-${gitRepositoryBranch}`;
};

export const getCommitTagOrHash = (
  commitHash: string,
  commitTags?: string[],
): string => commitTags?.[0] ?? commitHash;
