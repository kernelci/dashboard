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
  Warning,
  Error,
  Success,
  None,
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
      <ColoredCircle quantity={errors} type={ItemType.Error} />
    ) : (
      <></>
    );

  const itemWarning =
    warnings && warnings > 0 ? (
      <ColoredCircle quantity={warnings} type={ItemType.Warning} />
    ) : (
      <></>
    );

  const itemNeutral =
    !errors || errors === 0 || !success || success === 0 ? (
      <ColoredCircle quantity={0} type={ItemType.None} />
    ) : (
      <></>
    );

  const itemSuccess =
    success && success > 0 ? (
      <ColoredCircle quantity={success} type={ItemType.Success} />
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
