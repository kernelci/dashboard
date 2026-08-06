import type { Table } from '@tanstack/react-table';
import { ArrowDown, ArrowUp, Columns3 } from 'lucide-react';
import { FormattedMessage, useIntl } from 'react-intl';
import type { JSX } from 'react';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { getColumnLayoutMeta } from '@/utils/columnLayout';

type ColumnsMenuProps<TData> = {
  table: Table<TData>;
  moveColumn: (columnId: string, direction: -1 | 1) => void;
};

export const ColumnsMenu = <TData,>({
  table,
  moveColumn,
}: ColumnsMenuProps<TData>): JSX.Element => {
  const intl = useIntl();
  const columns = table.getAllLeafColumns();
  const order = table.getState().columnOrder;
  const orderedColumns =
    order.length > 0
      ? order
          .map(id => columns.find(column => column.id === id))
          .filter((column): column is (typeof columns)[number] => !!column)
      : columns;

  const menuColumns = orderedColumns.filter(column => {
    const canHide = column.getCanHide();
    const canReorder = !getColumnLayoutMeta(column.columnDef.meta).isRowHeader;
    return canHide || canReorder;
  });

  const movableIds = menuColumns
    .filter(column => !getColumnLayoutMeta(column.columnDef.meta).isRowHeader)
    .map(column => column.id);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Columns3 className="h-4 w-4" />
          <FormattedMessage id="table.columns" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-2">
        <ul className="flex flex-col gap-1">
          {menuColumns.map(column => {
            const meta = getColumnLayoutMeta(column.columnDef.meta);
            const canHide = column.getCanHide();
            const movableIndex = movableIds.indexOf(column.id);
            const canMoveUp = movableIndex > 0;
            const canMoveDown =
              movableIndex >= 0 && movableIndex < movableIds.length - 1;
            const label = meta.headerIntlKey
              ? intl.formatMessage({ id: meta.headerIntlKey })
              : column.id;

            return (
              <li
                key={column.id}
                className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-slate-50"
              >
                <Checkbox
                  checked={column.getIsVisible()}
                  disabled={!canHide}
                  onCheckedChange={value =>
                    column.toggleVisibility(value === true)
                  }
                  aria-label={intl.formatMessage(
                    { id: 'table.toggleColumn' },
                    { column: label },
                  )}
                />
                <span className="min-w-0 flex-1 truncate text-sm">{label}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  disabled={!canMoveUp}
                  onClick={() => moveColumn(column.id, -1)}
                  aria-label={intl.formatMessage({ id: 'table.moveColumnUp' })}
                >
                  <ArrowUp className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  disabled={!canMoveDown}
                  onClick={() => moveColumn(column.id, 1)}
                  aria-label={intl.formatMessage({
                    id: 'table.moveColumnDown',
                  })}
                >
                  <ArrowDown className="h-3.5 w-3.5" />
                </Button>
              </li>
            );
          })}
        </ul>
      </PopoverContent>
    </Popover>
  );
};
