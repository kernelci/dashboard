import classNames from 'classnames';
import { useMemo } from 'react';

import { Button } from '@/components/ui/button';
import { TableFilter } from '@/types/tree/TreeDetails';

interface ITableStatusFilter {
  onClick: (value: TableFilter) => void;
  filters: {
    label: string;
    value: TableFilter;
    isSelected: boolean;
  }[];
}

const TableStatusFilter = ({
  filters,
  onClick,
}: ITableStatusFilter): JSX.Element => {
  const filterButtons = useMemo(
    () =>
      filters.map((filter, index) => (
        <Button
          variant="outline"
          key={filter.label}
          className={classNames(
            'border border-black hover:bg-lightBlue',
            index === 0 ? 'rounded-l-full' : 'rounded-l-none',
            index === filters.length - 1 ? 'rounded-r-full' : 'rounded-r-none',
            filter.isSelected
              ? 'bg-blue text-white'
              : 'bg-transparent text-black',
          )}
          onClick={() => onClick(filter.value)}
        >
          {filter.label}
        </Button>
      )),
    [filters, onClick],
  );
  return <div>{filterButtons}</div>;
};

export default TableStatusFilter;
