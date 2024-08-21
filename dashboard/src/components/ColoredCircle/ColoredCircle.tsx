import { cn } from '../../lib/utils';

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
      className={cn(
        'inline-flex h-6 w-fit min-w-6 justify-center rounded-full px-1 text-black',
        className,
        backgroundClassName,
      )}
    >
      <span className="text-sm">{quantity}</span>
    </div>
  );
};

export default ColoredCircle;
