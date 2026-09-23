import type { JSX } from 'react';
import { useIntl } from 'react-intl';

import type {
  TableStatusOption,
  TableStatusSelection,
} from '@/utils/tableStatusFilter';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import TableStatusFilter from './TableStatusFilter';
import {
  TableGroupingControls,
  type ITableGroupingControls,
} from './TableGroupingControls';

interface ITableTopFilters {
  labels: Record<TableStatusOption, string>;
  selection: TableStatusSelection;
  onToggleFilter: (option: TableStatusOption) => void;
  currentPathFilter?: string;
  onSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  groupingControls?: ITableGroupingControls;
}

export function TableTopFilters({
  labels,
  selection,
  onToggleFilter,
  currentPathFilter,
  onSearchChange,
  groupingControls,
}: ITableTopFilters): JSX.Element {
  const intl = useIntl();

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:flex-wrap sm:items-end sm:gap-8">
      {/* `contents` keeps mobile ordering (status, grouping, search) while
          sm+ groups the status filter and search into a single row item */}
      <div className="contents sm:flex sm:items-end sm:gap-8">
        <TableStatusFilter
          labels={labels}
          selection={selection}
          onToggle={onToggleFilter}
        />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          startingValue={currentPathFilter}
          className="order-last w-9/10 sm:order-none sm:w-50"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      {groupingControls && (
        <div className="sm:ml-auto">
          <TableGroupingControls {...groupingControls} />
        </div>
      )}
    </div>
  );
}
