import { useCallback, useState } from 'react';
import cls from 'classnames';

interface ICheckbox {
  onToggle: (checked: boolean) => void;
  startChecked?: boolean;
  text: string;
  className?: string;
}

const containerClass =
  'min-w-[300px] p-4 border-[2px] border-darkGray rounded cursor-pointer text-dimGray';

const Checkbox = ({
  text,
  onToggle,
  className,
  startChecked = false,
}: ICheckbox): JSX.Element => {
  const [isChecked, setIsChecked] = useState(startChecked);

  const onClick = useCallback(() => {
    setIsChecked(state => !state);
    onToggle(!isChecked);
  }, [isChecked, onToggle]);

  return (
    <div
      className={cls(containerClass, className, {
        'border-lightBlue': isChecked,
      })}
      onClick={onClick}
    >
      <input type="checkbox" checked={isChecked} />
      <span className="ml-4">{text}</span>
    </div>
  );
};

export default Checkbox;
