import classNames from 'classnames';

import { ItemType } from '../ListingItem/ListingItem';

interface IColoredCircle {
  quantity: number;
  type: ItemType;
  className?: string;
}

const ColoredCircle = ({
  quantity,
  type,
  className,
}: IColoredCircle): JSX.Element => {
  const backgroundColor =
    type === ItemType.Error ? 'bg-lightRed' : 'bg-lightGreen';
  return (
    <div
      className={classNames(
        backgroundColor,
        'rounded-full text-black h-6 min-w-6 flex justify-center px-1',
        className,
      )}
    >
      <span className="text-sm">{quantity}</span>
    </div>
  );
};

export default ColoredCircle;
