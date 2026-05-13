const COMMIT_REGEX = [
  /\b[0-9a-f]{40}\b/g,
  /\S*v?\d+\.\d+(?:\.\d+)?(?:-rc\d+)?\S*/gi,
  /\b([a-z][a-z0-9]*(?:-[a-z0-9]+)*)-(\d{8})\S*/gi,
];

export const listCommits = (text: string): string[] => {
  if (typeof text !== 'string') {
    return [];
  }
  return COMMIT_REGEX.flatMap(r => text.match(r) || []);
};
