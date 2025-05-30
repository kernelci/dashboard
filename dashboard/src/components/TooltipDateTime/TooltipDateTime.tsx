import { format, formatDistanceToNow, isValid } from 'date-fns';

import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { getDateOffset } from '@/utils/utils';

type TooltipDateTimeProps = {
  dateTime: string | Date;
  dateFormat?: string;
  timeFormat?: string;
  lineBreak?: boolean;
  showLabelTime?: boolean;
  showLabelTZ?: boolean;
  showTooltip?: boolean;
  showRelative?: boolean;
  message?: string;
};

const TooltipDateTime = ({
  dateTime,
  dateFormat,
  timeFormat,
  lineBreak = true,
  showLabelTime,
  showLabelTZ = false,
  showTooltip = true,
  showRelative = false,
  message,
}: TooltipDateTimeProps): JSX.Element => {
  const dateObj = typeof dateTime === 'string' ? new Date(dateTime) : dateTime;
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
      <TooltipTrigger asChild>
        {showRelative ? (
          <div className="text-start">
            {message && <span className="pl-2">{message}</span>}
            <FormattedMessage
              id="global.timeAgo"
              values={{ time: formatDistanceToNow(dateObj) }}
            />
          </div>
        ) : (
          <span className="text-center">
            {date} {showLabelTime ? time : ''} {showLabelTZ ? tz : ''}
          </span>
        )}
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
