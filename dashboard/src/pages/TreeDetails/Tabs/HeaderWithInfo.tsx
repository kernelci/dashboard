import { FormattedMessage } from 'react-intl';
import { LiaQuestionCircle } from 'react-icons/lia';

import { MessagesKey, formattedBreakLineValue } from '@/locales/messages';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

interface IHeaderWithInfo {
  labelId: MessagesKey;
  tooltipId: MessagesKey;
}

const HeaderWithInfo = ({
  labelId,
  tooltipId,
}: IHeaderWithInfo): JSX.Element => (
  <span className="flex items-center gap-1">
    <FormattedMessage id={labelId} />
    <Tooltip>
      <TooltipTrigger>
        <LiaQuestionCircle />
      </TooltipTrigger>
      <TooltipContent>
        <FormattedMessage id={tooltipId} values={formattedBreakLineValue} />
      </TooltipContent>
    </Tooltip>
  </span>
);

export default HeaderWithInfo;
