import type { JSX } from 'react';

import { cn } from '@/lib/utils';
import { TooltipIcon } from '@/components/Icons/TooltipIcon';

export const IssueTooltip = ({
  iconClassName,
  tooltipClassName,
}: {
  iconClassName?: string;
  tooltipClassName?: string;
}): JSX.Element => {
  return (
    <TooltipIcon
      iconClassName={cn('h-5 w-5', iconClassName)}
      contentClassName={cn('font-normal', tooltipClassName)}
      tooltipId="issue.tooltip"
    />
  );
};
