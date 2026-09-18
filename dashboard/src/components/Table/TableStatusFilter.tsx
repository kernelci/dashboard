import type { JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import type {
  TableStatusOption,
  TableStatusSelection,
  TableStatusToggleValue,
} from '@/types/tree/TreeDetails';
import { tableStatusOptions } from '@/types/tree/TreeDetails';
import { FilterButton } from '@/components/Button/FilterButton';
import { isFullTableStatusSelection } from '@/utils/tableStatusFilter';

export type TStatusFilterChip = {
  label: string;
  value: TableStatusOption;
};

interface ITableStatusFilter {
  chips: TStatusFilterChip[];
  selection: TableStatusSelection;
  onToggle: (value: TableStatusToggleValue) => void;
}

const TableStatusFilter = ({
  chips,
  selection,
  onToggle,
}: ITableStatusFilter): JSX.Element => {
  const intl = useIntl();
  const allStatuses = isFullTableStatusSelection(selection);

  return (
    <div className="flex flex-col gap-2">
      <span className="text-dim-gray text-sm">
        <FormattedMessage id="filter.tableFilter" />
        {allStatuses && (
          <span className="text-dark-gray2 font-normal">
            {' '}
            <FormattedMessage id="filter.tableFilterAllStatuses" />
          </span>
        )}
      </span>
      <div
        className="flex flex-wrap gap-2"
        role="group"
        aria-label={intl.formatMessage({ id: 'filter.tableFilter' })}
      >
        <FilterButton selected={allStatuses} onClick={() => onToggle('all')}>
          <FormattedMessage id="filter.tableFilterAll" />
        </FilterButton>
        {chips.map(chip => (
          <FilterButton
            key={chip.value}
            selected={selection.includes(chip.value)}
            onClick={() => onToggle(chip.value)}
          >
            {chip.label}
          </FilterButton>
        ))}
      </div>
    </div>
  );
};

export default TableStatusFilter;

export const buildStatusFilterChips = (
  labels: Record<TableStatusOption, string>,
): TStatusFilterChip[] =>
  tableStatusOptions.map(value => ({
    value,
    label: labels[value],
  }));
