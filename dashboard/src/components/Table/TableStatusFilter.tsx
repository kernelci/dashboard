import type { JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { FilterButton } from '@/components/Button/FilterButton';
import {
  tableStatusOptions,
  type TableStatusOption,
  type TableStatusSelection,
} from '@/utils/tableStatusFilter';

interface ITableStatusFilter {
  labels: Record<TableStatusOption, string>;
  selection: TableStatusSelection;
  onToggle: (value: TableStatusOption) => void;
}

const TableStatusFilter = ({
  labels,
  selection,
  onToggle,
}: ITableStatusFilter): JSX.Element => {
  const intl = useIntl();

  return (
    <div className="flex flex-col gap-2">
      <span className="text-dim-gray text-sm">
        <FormattedMessage id="filter.tableFilter" />
      </span>
      <div
        className="flex flex-wrap gap-2"
        role="group"
        aria-label={intl.formatMessage({ id: 'filter.tableFilter' })}
      >
        {tableStatusOptions.map(value => (
          <FilterButton
            key={value}
            selected={selection.includes(value)}
            onClick={() => onToggle(value)}
          >
            {labels[value]}
          </FilterButton>
        ))}
      </div>
    </div>
  );
};

export default TableStatusFilter;
