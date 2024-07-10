import classNames from 'classnames';

interface IColoredCircle {
  quantity?: number;
  className?: string;
  backgroundClassName: string;
}

const ColoredCircle = ({
  quantity,
  backgroundClassName,
  className,
}: IColoredCircle): JSX.Element => {
  return (
    <div
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
