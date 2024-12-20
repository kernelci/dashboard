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
