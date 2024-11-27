import classNames from 'classnames';

import { useCallback, Fragment, memo } from 'react';

import type { PropsWithChildren } from 'react';

import ColoredCircle from '../ColoredCircle/ColoredCircle';
import { Tooltip, TooltipContent, TooltipTrigger } from '../Tooltip';

export interface IListingItem {
  leftIcon?: React.ReactNode;
  warnings?: number;
  errors?: number;
  success?: number;
  unknown?: number;
  text: string;
  hasBottomBorder?: boolean;
  showNumber?: boolean;
  onClick?: (item: string) => void;
  tooltip?: string;
  disabled?: boolean; // temporary solution
}

export enum ItemType {
  Warning = 'bg-yellow',
  Error = 'bg-lightRed',
  Success = 'bg-lightGreen',
  Unknown = 'bg-mediumGray',
  None = 'bg-lightGray',
}

// TODO Add Tooltip text
const ListingItem = ({
  leftIcon,
  warnings,
  errors,
  text,
  success,
  unknown,
  hasBottomBorder,
  showNumber = true,
  onClick,
  tooltip,
  disabled,
}: IListingItem): JSX.Element => {
  const hasBorder = hasBottomBorder
    ? '[&:not(:last-child)]:border-b [&:not(:last-child)]:pb-2 [&:not(:last-child)]:mb-2'
    : '';
  const hasErrors = errors && errors > 0 && showNumber;
  const hasWarnings = warnings && warnings > 0 && showNumber;
  const hasSuccess = success && success > 0 && showNumber;
  const hasUnknown = unknown && unknown > 0 && showNumber;
  const hasNone =
    !leftIcon &&
    !hasErrors &&
    !hasWarnings &&
    !hasSuccess &&
    !hasUnknown &&
    showNumber;

  const handleOnClick = useCallback(() => {
    if (onClick && !disabled) {
      onClick(text);
    }
  }, [disabled, onClick, text]);

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

  const TooltipComponent = ({ children }: PropsWithChildren): JSX.Element => {
    return (
      <Tooltip>
        <div className="flex">
          <TooltipTrigger className="overflow-hidden">
            {children}
          </TooltipTrigger>

          <TooltipContent>
            <span className="text-sm text-black">{tooltip}</span>
          </TooltipContent>
        </div>
      </Tooltip>
    );
  };

  const TooltipMemoized = memo(TooltipComponent);

  const WrapperComponent = onClick ? 'button' : 'div';
  const TooltipWrapper = tooltip ? TooltipMemoized : Fragment;

  return (
    <TooltipWrapper>
      <WrapperComponent
        className={classNames(
          'flex flex-row items-center gap-2 pb-1',
          hasBorder,
        )}
        disabled={disabled}
        onClick={handleOnClick}
      >
        {itemError}
        {itemWarning}
        {itemSuccess}
        {itemUnknown}
        {itemNeutral}
        {leftIcon}
        <span className="truncate text-sm text-black">{text}</span>
      </WrapperComponent>
    </TooltipWrapper>
  );
};

export default ListingItem;
