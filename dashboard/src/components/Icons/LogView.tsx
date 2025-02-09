import { MdOutlineFileOpen } from 'react-icons/md';

import { FormattedMessage } from 'react-intl';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

export const LogViewIcon = (): JSX.Element => (
  <Tooltip>
    <TooltipTrigger>
      <MdOutlineFileOpen className="text-lg font-bold text-blue" />
    </TooltipTrigger>
    <TooltipContent>
      <FormattedMessage id="global.viewLog" />
    </TooltipContent>
  </Tooltip>
);
