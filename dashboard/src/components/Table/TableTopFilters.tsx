import type { JSX } from 'react';
import { useIntl } from 'react-intl';

import type {
  TableStatusSelection,
  TableStatusToggleValue,
} from '@/types/tree/TreeDetails';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import type { TStatusFilterChip } from './TableStatusFilter';
import TableStatusFilter from './TableStatusFilter';
import {
  TableGroupingControls,
  type ITableGroupingControls,
} from './TableGroupingControls';

interface ITableTopFilters {
  chips: TStatusFilterChip[];
  selection: TableStatusSelection;
  onToggleFilter: (option: TableStatusToggleValue) => void;
  currentPathFilter?: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  groupingControls?: ITableGroupingControls;
}

export function TableTopFilters({
  chips,
  selection,
  onToggleFilter,
  currentPathFilter,
  onSearchChange,
  groupingControls,
}: ITableTopFilters): JSX.Element {
  const intl = useIntl();

  return (
    <div className="flex w-full flex-col gap-4">
      <div className="flex w-full flex-col gap-4 lg:flex-row lg:flex-wrap lg:items-end lg:justify-between">
        <TableStatusFilter
          chips={chips}
          selection={selection}
          onToggle={onToggleFilter}
        />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          startingValue={currentPathFilter}
          className="w-full min-w-0 lg:max-w-md"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      {groupingControls && (
        <div className="flex justify-end">
          <TableGroupingControls {...groupingControls} />
        </div>
      )}
    </div>
  );
}
