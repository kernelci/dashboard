interface TreeIdentifierParams {
  treeName: string;
  gitRepositoryUrl?: string;
  gitRepositoryBranch: string;
  separator?: string;
}

export const makeTreeIdentifierKey = ({
  treeName,
  gitRepositoryUrl,
  gitRepositoryBranch,
  separator = '-',
}: TreeIdentifierParams): string => {
  return [treeName, gitRepositoryUrl, gitRepositoryBranch]
    .filter(value => value !== undefined)
    .join(separator);
};

export const getCommitTagOrHash = (
  commitHash: string,
  commitTags?: string[],
): string => commitTags?.[0] ?? commitHash;
