import type { JSX } from 'react';

import { LiaQuestionCircle } from 'react-icons/lia';
import { FormattedMessage } from 'react-intl';

import { formattedBreakLineValue, type MessagesKey } from '@/locales/messages';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

export const TooltipIcon = ({
  triggerClassName,
  iconClassName,
  contentClassName,
  tooltipId,
  tooltipValues,
}: {
  triggerClassName?: string;
  iconClassName?: string;
  contentClassName?: string;
  tooltipId: MessagesKey;
  tooltipValues?: Record<string, unknown>;
}): JSX.Element => {
  return (
    <Tooltip>
      <TooltipTrigger className={triggerClassName}>
        <LiaQuestionCircle className={iconClassName} />
      </TooltipTrigger>
      <TooltipContent className={contentClassName}>
        <FormattedMessage
          id={tooltipId}
          values={{ ...formattedBreakLineValue, ...tooltipValues }}
        />
      </TooltipContent>
    </Tooltip>
  );
};
