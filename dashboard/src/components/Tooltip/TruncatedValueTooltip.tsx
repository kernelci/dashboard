import { truncateBigText, truncateUrl, valueOrEmpty } from '@/lib/string';

import { cn } from '@/lib/utils';

import { Tooltip, TooltipContent, TooltipTrigger } from './Tooltip';

export const TruncatedValueTooltip = ({
  value,
  isUrl = false,
}: {
  value: string | undefined;
  isUrl?: boolean;
}): JSX.Element => {
  if (!value) {
    return <span>{valueOrEmpty(value)}</span>;
  }

  return (
    <Tooltip>
      <TooltipTrigger
        className={cn('', isUrl ? 'cursor-pointer' : 'cursor-default')}
      >
        {isUrl ? truncateUrl(value) : truncateBigText(value)}
      </TooltipTrigger>
      <TooltipContent className="max-w-2xl overflow-auto">
        {value}
      </TooltipContent>
    </Tooltip>
  );
};
