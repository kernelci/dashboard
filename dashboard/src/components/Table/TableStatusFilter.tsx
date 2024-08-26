import classNames from 'classnames';
import { useMemo } from 'react';

import { Button } from '@/components/ui/button';
import { TableFilter } from '@/types/tree/TreeDetails';

interface ITableStatusFilter {
  onClick: (value: TableFilter) => void;
  filters: {
    label: string;
    value: TableFilter;
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
            'border border-black',
            index === 0 ? 'rounded-l-full' : 'rounded-l-none',
            index === filters.length - 1 ? 'rounded-r-full' : 'rounded-r-none',
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
