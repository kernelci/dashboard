import { format, isValid } from 'date-fns';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { getDateOffset } from '@/utils/utils';

type TooltipDateTimeProps = {
  dateTime: string;
  dateFormat?: string;
  timeFormat?: string;
  lineBreak?: boolean;
  showLabelTime?: boolean;
  showLabelTZ?: boolean;
  showTooltip?: boolean;
};

const TooltipDateTime = ({
  dateTime,
  dateFormat,
  timeFormat,
  lineBreak = true,
  showLabelTime,
  showLabelTZ = false,
  showTooltip = true,
}: TooltipDateTimeProps): JSX.Element => {
  const dateObj = new Date(dateTime);
  if (!isValid(dateObj)) {
    return <div>-</div>;
  }

  const date = dateFormat
    ? format(dateObj, dateFormat)
    : dateObj.toLocaleDateString();
  const time = timeFormat
    ? format(dateObj, timeFormat)
    : dateObj.toLocaleTimeString();
  const tz = getDateOffset(dateObj);

  return (
    <Tooltip>
      <TooltipTrigger>
        <div>
          {date} {showLabelTime ? time : ''} {showLabelTZ ? tz : ''}
        </div>
      </TooltipTrigger>
      {showTooltip && (
        <TooltipContent>
          <div className="text-center">
            {date}
            {lineBreak ? <br /> : ' '}
            {time} {tz}
          </div>
        </TooltipContent>
      )}
    </Tooltip>
  );
};

export default TooltipDateTime;
