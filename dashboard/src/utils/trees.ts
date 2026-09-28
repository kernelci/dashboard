interface TreeIdentifierParams {
  treeName: string;
  gitRepositoryUrl?: string;
  gitRepositoryBranch: string;
  origin?: string;
  separator?: string;
}

export const makeTreeIdentifierKey = ({
  treeName,
  gitRepositoryUrl,
  gitRepositoryBranch,
  origin,
  separator = '-',
}: TreeIdentifierParams): string => {
  const parts = [treeName, gitRepositoryUrl, gitRepositoryBranch];
  if (origin) {
    parts.push(origin);
  }
  return parts.filter(value => value !== undefined).join(separator);
};

export const getCommitTagOrHash = (
  commitHash: string,
  commitTags?: string[],
): string => commitTags?.[0] ?? commitHash;
