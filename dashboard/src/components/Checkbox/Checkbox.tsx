import cls from 'classnames';

import type { JSX } from 'react';

import {
  isUrl,
  shouldTruncate,
  truncateBigText,
  truncateUrl,
} from '@/lib/string';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

interface ICheckbox {
  onToggle: () => void;
  isChecked?: boolean;
  text: string;
  className?: string;
}

const containerClass =
  'min-w-[300px] p-4 border-[2px] border-dark-gray rounded-sm cursor-pointer text-dim-gray';

const maxCheckboxLength = 29;

const Checkbox = ({
  text,
  onToggle,
  className,
  isChecked = false,
}: ICheckbox): JSX.Element => {
  let truncatedText = text;
  const shouldTruncateResult = shouldTruncate(text, maxCheckboxLength);
  if (shouldTruncateResult) {
    if (isUrl(text)) {
      truncatedText = truncateUrl(text);
    } else {
      truncatedText = truncateBigText(text, maxCheckboxLength);
    }
  }

  return (
    <label
      className={cls(containerClass, className, {
        'border-blue': isChecked,
      })}
    >
      <input type="checkbox" checked={isChecked} onChange={onToggle} />
      {shouldTruncateResult ? (
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="ml-4">{truncatedText}</span>
          </TooltipTrigger>
          <TooltipContent>{text}</TooltipContent>
        </Tooltip>
      ) : (
        <span className="ml-4">{truncatedText}</span>
      )}
    </label>
  );
};

export default Checkbox;
