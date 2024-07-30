import classNames from 'classnames';

interface IColoredCircle {
  tooltipText?: string;
  quantity?: number;
  className?: string;
  backgroundClassName: string;
}

const ColoredCircle = ({
  quantity,
  backgroundClassName,
  className,
  tooltipText,
}: IColoredCircle): JSX.Element => {
  return (
    <div
      title={tooltipText}
      className={classNames(
        'rounded-full text-black h-6 min-w-6 flex justify-center px-1',
        className,
        backgroundClassName,
      )}
    >
      <span className="text-sm">{quantity}</span>
    </div>
  );
};

export default ColoredCircle;
