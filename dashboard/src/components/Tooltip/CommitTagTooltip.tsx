import { Tooltip, TooltipTrigger, TooltipContent } from './Tooltip';

export const CommitTagTooltip = ({
  commitName,
  commitHash,
  commitTags,
}: {
  commitName: string | undefined;
  commitHash: string | undefined;
  commitTags: string[] | undefined;
}): JSX.Element => {
  let hover;
  let content;

  if (commitTags !== undefined && commitTags.length > 0) {
    content = commitTags[0];
    hover = commitHash ?? commitName ?? '';
  } else {
    content = commitHash ?? commitName ?? '';
    hover = commitName ?? '';
  }

  return (
    <Tooltip>
      <TooltipTrigger>{content}</TooltipTrigger>
      <TooltipContent>{hover}</TooltipContent>
    </Tooltip>
  );
};
