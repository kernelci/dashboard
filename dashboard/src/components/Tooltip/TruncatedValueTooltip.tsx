import type { JSX } from 'react';

import { truncateBigText, truncateUrl, valueOrEmpty } from '@/lib/string';

import { cn } from '@/lib/utils';

import { Tooltip, TooltipContent, TooltipTrigger } from './Tooltip';

export const TruncatedValueTooltip = ({
  value,
  isUrl = false,
  isClickable = false,
}: {
  value: string | undefined;
  isUrl?: boolean;
  isClickable?: boolean;
}): JSX.Element => {
  if (!value) {
    return <span>{valueOrEmpty(value)}</span>;
  }

  return (
    <Tooltip>
      <TooltipTrigger
        className={cn(
          '',
          isClickable || isUrl ? 'cursor-pointer' : 'cursor-default',
        )}
      >
        {isUrl ? truncateUrl(value) : truncateBigText(value)}
      </TooltipTrigger>
      <TooltipContent className="max-w-2xl overflow-auto">
        {value}
      </TooltipContent>
    </Tooltip>
  );
};
