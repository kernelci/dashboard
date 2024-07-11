import { useMemo } from 'react';

import ListingComponentItem, {
  IListingComponentItem,
} from '@/components/ListingComponentItem/ListingComponentItem';

import BaseCard from '../BaseCard';

export interface IListingComponent {
  items: IListingComponentItem[];
  title: string;
}

interface IListedComponent {
  items: IListingComponentItem[];
}

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
