import { ReactElement, ReactNode, useMemo } from 'react';

import ListingItem, {
  IListingItem,
} from '@/components/ListingItem/ListingItem';

export interface IListingContent {
  items: IListingItem[];
  title: ReactElement;
  type: 'listing';
}

interface IListingCardContent {
  items: IListingItem[];
}

interface DumbListingContent {
  children: ReactNode;
}
export const DumbListingContent = ({
  children,
}: DumbListingContent): JSX.Element => {
  return <div className="flex flex-col gap-2 p-4">{children}</div>;
};

const ListingContent = ({ items }: IListingCardContent): JSX.Element => {
  const content = useMemo(() => {
    return items.map(item => (
      <ListingItem
        key={item.text}
        warnings={item.warnings}
        errors={item.errors}
        success={item.success}
        text={item.text}
      />
    ));
  }, [items]);
  return <DumbListingContent>{content}</DumbListingContent>;
};

export default ListingContent;
