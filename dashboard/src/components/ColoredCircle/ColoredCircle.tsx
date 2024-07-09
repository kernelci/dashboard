import classNames from 'classnames';

import { ComponentType } from '@/components/Cards/ListingComponentCard/ListingComponentCard';

interface IColoredCircle {
  quantity: number;
  type: ComponentType;
}

const ColoredCircle = ({ quantity, type }: IColoredCircle): JSX.Element => {
  const backgroundColor =
    type === ComponentType.Error ? 'bg-lightRed' : 'bg-yellow';
  return (
    <div
      className={classNames(
        backgroundColor,
        'rounded-full text-black h-6 min-w-6 flex justify-center px-1',
      )}
    >
      <span className="text-sm">{quantity}</span>
    </div>
  );
};

export default ColoredCircle;
