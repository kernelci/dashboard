import classNames from 'classnames';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

export interface IListingItem {
  warnings?: number;
  errors?: number;
  success?: number;
  text?: string;
  hasBottomBorder?: boolean;
}

export enum ItemType {
  Warning = 'bg-yellow',
  Error = 'bg-lightRed',
  Success = 'bg-lightGreen',
  None = 'bg-mediumGray',
}

const ListingItem = ({
  warnings,
  errors,
  text,
  success,
  hasBottomBorder,
}: IListingItem): JSX.Element => {
  const hasBorder = hasBottomBorder ? 'border-b' : '';
  const itemError =
    errors && errors > 0 ? (
      <ColoredCircle quantity={errors} backgroundClassName={ItemType.Error} />
    ) : (
      <></>
    );

  const itemWarning =
    warnings && warnings > 0 ? (
      <ColoredCircle
        quantity={warnings}
        backgroundClassName={ItemType.Warning}
      />
    ) : (
      <></>
    );

  const itemNeutral =
    !errors || errors === 0 || !success || success === 0 ? (
      <ColoredCircle quantity={0} backgroundClassName={ItemType.None} />
    ) : (
      <></>
    );

  const itemSuccess =
    success && success > 0 ? (
      <ColoredCircle
        quantity={success}
        backgroundClassName={ItemType.Success}
      />
    ) : (
      <></>
    );

  return (
    <div className={classNames('flex flex-row gap-2 pb-1', hasBorder)}>
      {itemError}
      {itemWarning}
      {itemSuccess}
      {itemNeutral}
      <span className="text-black text-sm">{text}</span>
    </div>
  );
};

export default ListingItem;
