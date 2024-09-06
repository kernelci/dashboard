import cls from 'classnames';

interface ICheckbox {
  onToggle: () => void;
  isChecked?: boolean;
  text: string;
  className?: string;
}

const containerClass =
  'min-w-[300px] p-4 border-[2px] border-darkGray rounded cursor-pointer text-dimGray';

const Checkbox = ({
  text,
  onToggle,
  className,
  isChecked = false,
}: ICheckbox): JSX.Element => {
  return (
    <label
      className={cls(containerClass, className, {
        'border-blue': isChecked,
      })}
    >
      <input type="checkbox" checked={isChecked} onChange={onToggle} />
      <span className="ml-4">{text}</span>
    </label>
  );
};

export default Checkbox;
