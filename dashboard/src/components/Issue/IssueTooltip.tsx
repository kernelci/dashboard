import { LiaQuestionCircle } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { formattedBreakLineValue } from '@/locales/messages';
import { cn } from '@/lib/utils';

export const IssueTooltip = ({
  iconClassName,
  tooltipClassName,
}: {
  iconClassName?: string;
  tooltipClassName?: string;
}): JSX.Element => {
  return (
    <Tooltip>
      <TooltipTrigger>
        <LiaQuestionCircle className={cn('h-5 w-5', iconClassName)} />
      </TooltipTrigger>
      <TooltipContent className={cn('font-normal', tooltipClassName)}>
        <FormattedMessage id="issue.tooltip" values={formattedBreakLineValue} />
      </TooltipContent>
    </Tooltip>
  );
};
