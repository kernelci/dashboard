import classNames from 'classnames';
import { useCallback, useMemo } from 'react';

import { Button } from '@/components/ui/button';

import type { BuildsTableFilter, TestsTableFilter } from '@/types/general';

interface ITableStatusFilter {
  onClickBuild?: (value: BuildsTableFilter) => void;
  onClickTest?: (value: TestsTableFilter) => void;
  filters: {
    label: string;
    value: BuildsTableFilter | TestsTableFilter;
    isSelected: boolean;
  }[];
}

const TableStatusFilter = ({
  filters,
  onClickBuild,
  onClickTest,
}: ITableStatusFilter): JSX.Element => {
  const onClickFilter = useCallback(
    (filter: BuildsTableFilter | TestsTableFilter) => {
      onClickBuild?.(filter as BuildsTableFilter);
      onClickTest?.(filter as TestsTableFilter);
    },
    [onClickBuild, onClickTest],
  );

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
          onClick={() => onClickFilter(filter.value)}
        >
          {filter.label}
        </Button>
      )),
    [filters, onClickFilter],
  );
  return <div>{filterButtons}</div>;
};

export default TableStatusFilter;
