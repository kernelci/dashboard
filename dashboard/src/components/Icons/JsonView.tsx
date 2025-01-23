import { AiOutlineFileSearch } from 'react-icons/ai';

import { FormattedMessage } from 'react-intl';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

export const JsonViewIcon = (): JSX.Element => (
  <Tooltip>
    <TooltipTrigger>
      <AiOutlineFileSearch className="text-lg text-blue" />
    </TooltipTrigger>
    <TooltipContent>
      <FormattedMessage id="global.viewJson" />
    </TooltipContent>
  </Tooltip>
);
