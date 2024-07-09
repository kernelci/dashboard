import { useMemo } from 'react';

import classNames from 'classnames';

import BaseCard from '../BaseCard';
import ColoredCircle from '../../ColoredCircle/ColoredCircle';

export interface IListingComponent {
  items: IListingComponentItem[];
  title: string;
}

interface IListingComponentItem {
  warnings?: number;
  errors?: number;
  text?: string;
  hasBottomBorder?: boolean;
}

interface IListedComponent {
  items: IListingComponentItem[];
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

const ListedContent = ({ items }: IListedComponent): JSX.Element => {
  const content = useMemo(() => {
    return items.map(item => (
      <ListingComponentItem
        key={item.text}
        warnings={item.warnings}
        errors={item.errors}
        text={item.text}
      />
    ));
  }, [items]);
  return <div className="flex flex-col gap-2 pt-2">{content}</div>;
};

const ListingComponentCard = ({
  title,
  items,
}: IListingComponent): JSX.Element => {
  return (
    <BaseCard
      className="!w-[400px]"
      title={title}
      content={<ListedContent items={items} />}
    />
  );
};

export default ListingComponentCard;
