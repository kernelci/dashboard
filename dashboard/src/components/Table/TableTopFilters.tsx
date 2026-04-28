import type { JSX } from 'react';
import { useIntl } from 'react-intl';

import type { PossibleTableFilters } from '@/types/tree/TreeDetails';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import type { TStatusFilters } from './TableStatusFilter';
import TableStatusFilter from './TableStatusFilter';

interface ITableTopFilters {
  filters: TStatusFilters[];
  onClickFilter: (newFilter: PossibleTableFilters) => void;
  currentPathFilter?: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export function TableTopFilters({
  filters,
  onClickFilter,
  currentPathFilter,
  onSearchChange,
}: ITableTopFilters): JSX.Element {
  const intl = useIntl();

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:gap-8">
      <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
      <DebounceInput
        debouncedSideEffect={onSearchChange}
        startingValue={currentPathFilter}
        className="w-9/10 sm:mt-6 sm:w-50"
        type="text"
        placeholder={intl.formatMessage({ id: 'global.search' })}
      />
    </div>
  );
}
