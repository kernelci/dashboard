import { AiOutlineFileSearch } from 'react-icons/ai';

import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

export const JsonViewIcon = (): JSX.Element => (
  <Tooltip>
    <TooltipTrigger>
      <AiOutlineFileSearch className="text-blue text-lg" />
    </TooltipTrigger>
    <TooltipContent>
      <FormattedMessage id="global.viewJson" />
    </TooltipContent>
  </Tooltip>
);
