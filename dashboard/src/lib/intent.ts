import { listCommits } from '@/lib/commits';

export type SearchIntent =
  | { intent: 'commits'; commits: string[]; search: string }
  | { intent: 'text'; search: string };

export const parseSearchIntent = (text: string): SearchIntent => {
  const commitList = listCommits(text);
  if (commitList.length > 0) {
    return {
      intent: 'commits',
      commits: commitList,
      search: commitList
        .reduce((acc, word) => acc.replace(word, ''), text)
        .trim(),
    };
  }
  return {
    intent: 'text',
    search: text,
  };
};
