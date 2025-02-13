import { FormattedMessage } from 'react-intl';

import { LiaQuestionCircleSolid } from 'react-icons/lia';

import type { JSX } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

export const LogspecInfoIcon = (): JSX.Element => (
  <Tooltip>
    <TooltipTrigger>
      <LiaQuestionCircleSolid className="h-5 w-5" />
    </TooltipTrigger>
    <TooltipContent>
      <FormattedMessage id="logspec.info" />
    </TooltipContent>
  </Tooltip>
);
