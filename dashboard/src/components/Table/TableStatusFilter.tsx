import classNames from 'classnames';
import { useCallback, useMemo, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { Button } from '@/components/ui/button';
import type { PossibleTableFilters } from '@/types/tree/TreeDetails';

interface ITableStatusFilter {
  onClickBuild?: (value: PossibleTableFilters) => void;
  onClickTest?: (value: PossibleTableFilters) => void;
  filters: {
    label: string;
    value: PossibleTableFilters;
    isSelected: boolean;
  }[];
}

const TableStatusFilter = ({
  filters,
  onClickBuild,
  onClickTest,
}: ITableStatusFilter): JSX.Element => {
  const onClickFilter = useCallback(
    (filter: PossibleTableFilters) => {
      onClickBuild?.(filter);
      onClickTest?.(filter);
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
            'hover:bg-light-blue border border-black',
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
  return (
    <div className="flex flex-col">
      <span className="ml-4">
        <FormattedMessage id="filter.tableFilter" />
      </span>
      <span>{filterButtons}</span>
    </div>
  );
};

export default TableStatusFilter;
