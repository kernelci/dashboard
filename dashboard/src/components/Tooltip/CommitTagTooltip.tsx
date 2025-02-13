import type { JSX } from 'react';

import CopyButton from '@/components/Button/CopyButton';

import { Tooltip, TooltipTrigger, TooltipContent } from './Tooltip';

export interface gitValues {
  commitTags?: string[];
  commitHash?: string;
  commitName?: string;
}

export const gitCommitValueSelector = ({
  commitTags,
  commitHash,
  commitName,
}: gitValues): { content: string; hover: string } => {
  let content;
  let hover;
  if (commitTags && commitTags.length > 0) {
    content = commitTags[0];
    hover = commitHash ?? commitName ?? '';
  } else {
    content = commitHash ?? commitName ?? '';
    hover = commitName ?? '';
  }
  return { content, hover };
};

interface ICommitTagTooltip {
  commitName?: string;
  commitHash?: string;
  commitTags?: string[];
  copyButton?: boolean;
}

export const CommitTagTooltip = ({
  commitName,
  commitHash,
  commitTags,
  copyButton = false,
}: ICommitTagTooltip): JSX.Element => {
  const { content, hover } = gitCommitValueSelector({
    commitTags: commitTags,
    commitHash: commitHash,
    commitName: commitName,
  });

  return (
    <>
      <Tooltip>
        <TooltipTrigger>{content}</TooltipTrigger>
        <TooltipContent>{hover}</TooltipContent>
      </Tooltip>
      {copyButton && <CopyButton value={content} />}
    </>
  );
};
