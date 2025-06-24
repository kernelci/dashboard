import type { JSX } from 'react';

import { LiaQuestionCircle } from 'react-icons/lia';
import { FormattedMessage } from 'react-intl';

import { formattedBreakLineValue, type MessagesKey } from '@/locales/messages';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { cn } from '@/lib/utils';

export const TooltipIcon = ({
  triggerClassName,
  iconClassName,
  contentClassName,
  tooltipId,
  tooltipValues,
  icon,
}: {
  triggerClassName?: string;
  iconClassName?: string;
  contentClassName?: string;
  tooltipId: MessagesKey;
  tooltipValues?: Record<string, unknown>;
  icon?: JSX.Element;
}): JSX.Element => {
  return (
    <Tooltip>
      <TooltipTrigger className={triggerClassName}>
        {icon ?? <LiaQuestionCircle className={iconClassName} />}
      </TooltipTrigger>
      <TooltipContent className={cn('whitespace-pre-line', contentClassName)}>
        <FormattedMessage
          id={tooltipId}
          values={{ ...formattedBreakLineValue, ...tooltipValues }}
        />
      </TooltipContent>
    </Tooltip>
  );
};
