import classNames from 'classnames';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

export interface IListingComponentItem {
  warnings?: number;
  errors?: number;
  text?: string;
  hasBottomBorder?: boolean;
}

export enum ComponentType {
  Warning,
  Error,
}

const ListingComponentItem = ({
  warnings,
  errors,
  text,
  hasBottomBorder,
}: IListingComponentItem): JSX.Element => {
  const hasBorder = hasBottomBorder ? 'border-b' : '';
  const itemError =
    errors && errors > 0 ? (
      <ColoredCircle quantity={errors} type={ComponentType.Error} />
    ) : (
      <></>
    );

  const itemWarning =
    warnings && warnings > 0 ? (
      <ColoredCircle quantity={warnings} type={ComponentType.Warning} />
    ) : (
      <></>
    );

  return (
    <div className={classNames('flex flex-row gap-2 pb-1', hasBorder)}>
      {itemError}
      {itemWarning}
      <span className="text-black text-sm">{text}</span>
    </div>
  );
};

export default ListingComponentItem;
