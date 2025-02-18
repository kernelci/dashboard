import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { Badge } from '@/components/ui/badge';

interface BranchBadgeProps {
  tag: string;
  className?: string;
}

export const BranchBadge = ({
  tag,
  className,
}: BranchBadgeProps): JSX.Element => (
  <Tooltip key={tag}>
    <TooltipTrigger className="cursor-default">
      <Badge variant="blueTag" className={className}>
        {tag}
      </Badge>
    </TooltipTrigger>
    <TooltipContent>
      <FormattedMessage id="issue.alsoPresentTooltip" values={{ tree: tag }} />
    </TooltipContent>
  </Tooltip>
);
