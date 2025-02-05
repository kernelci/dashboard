import cls from 'classnames';

import { isUrl, truncateBigText, truncateUrl } from '@/lib/string';

interface ICheckbox {
  onToggle: () => void;
  isChecked?: boolean;
  text: string;
  className?: string;
}

const containerClass =
  'min-w-[300px] p-4 border-[2px] border-darkGray rounded cursor-pointer text-dimGray';

const maxCheckboxLength = 30;

const Checkbox = ({
  text,
  onToggle,
  className,
  isChecked = false,
}: ICheckbox): JSX.Element => {
  let truncatedText = text;
  if (isUrl(text)) {
    truncatedText = truncateUrl(text);
  } else {
    truncatedText = truncateBigText(text, maxCheckboxLength);
  }

  return (
    <label
      className={cls(containerClass, className, {
        'border-blue': isChecked,
      })}
    >
      <input type="checkbox" checked={isChecked} onChange={onToggle} />
      <span className="ml-4">{truncatedText}</span>
    </label>
  );
};

export default Checkbox;
