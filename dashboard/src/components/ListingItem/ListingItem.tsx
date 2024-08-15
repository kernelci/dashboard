import classNames from 'classnames';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

export interface IListingItem {
  warnings?: number;
  errors?: number;
  success?: number;
  text?: string;
  hasBottomBorder?: boolean;
  showNumber?: boolean;
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
  showNumber = true,
}: IListingItem): JSX.Element => {
  const hasBorder = hasBottomBorder
    ? '[&:not(:last-child)]:border-b [&:not(:last-child)]:pb-2 [&:not(:last-child)]:mb-2'
    : '';
  const hasErrors = errors && errors > 0 && showNumber;
  const hasWarnings = warnings && warnings > 0 && showNumber;
  const hasSuccess = success && success > 0 && showNumber;
  const hasNone = !hasErrors && !hasWarnings && !hasSuccess && showNumber;

  const itemError = hasErrors ? (
    <ColoredCircle quantity={errors} backgroundClassName={ItemType.Error} />
  ) : (
    <></>
  );

  const itemWarning = hasWarnings ? (
    <ColoredCircle quantity={warnings} backgroundClassName={ItemType.Warning} />
  ) : (
    <></>
  );

  const itemNeutral = hasNone ? (
    <div>
      <ColoredCircle quantity={0} backgroundClassName={ItemType.None} />
    </div>
  ) : (
    <></>
  );

  const itemSuccess = hasSuccess ? (
    <ColoredCircle quantity={success} backgroundClassName={ItemType.Success} />
  ) : (
    <></>
  );

  return (
    <div className={classNames('flex flex-row gap-2 pb-1', hasBorder)}>
      {itemError}
      {itemWarning}
      {itemSuccess}
      {itemNeutral}
      <span className="text-sm text-black">{text}</span>
    </div>
  );
};

export default ListingItem;
