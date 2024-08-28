import classNames from 'classnames';

import { useCallback } from 'react';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

export interface IListingItem {
  warnings?: number;
  errors?: number;
  success?: number;
  unknown?: number;
  text: string;
  hasBottomBorder?: boolean;
  showNumber?: boolean;
  onClick?: (item: string) => void;
}

export enum ItemType {
  Warning = 'bg-yellow',
  Error = 'bg-lightRed',
  Success = 'bg-lightGreen',
  Unknown = 'bg-mediumGray',
  None = 'bg-lightGray',
}

const ListingItem = ({
  warnings,
  errors,
  text,
  success,
  unknown,
  hasBottomBorder,
  showNumber = true,
  onClick,
}: IListingItem): JSX.Element => {
  const hasBorder = hasBottomBorder
    ? '[&:not(:last-child)]:border-b [&:not(:last-child)]:pb-2 [&:not(:last-child)]:mb-2'
    : '';
  const hasErrors = errors && errors > 0 && showNumber;
  const hasWarnings = warnings && warnings > 0 && showNumber;
  const hasSuccess = success && success > 0 && showNumber;
  const hasUnknown = unknown && unknown > 0 && showNumber;
  const hasNone =
    !hasErrors && !hasWarnings && !hasSuccess && !hasUnknown && showNumber;

  const handleOnClick = useCallback(() => {
    if (onClick) {
      onClick(text);
    }
  }, [onClick, text]);

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

  const itemUnknown = hasUnknown ? (
    <ColoredCircle quantity={unknown} backgroundClassName={ItemType.Unknown} />
  ) : (
    <></>
  );

  const WrapperComponent = onClick ? 'button' : 'div';

  return (
    <WrapperComponent
      className={classNames('flex flex-row gap-2 pb-1', hasBorder)}
      onClick={handleOnClick}
    >
      {itemError}
      {itemWarning}
      {itemSuccess}
      {itemUnknown}
      {itemNeutral}
      <span className="text-sm text-black">{text}</span>
    </WrapperComponent>
  );
};

export default ListingItem;
