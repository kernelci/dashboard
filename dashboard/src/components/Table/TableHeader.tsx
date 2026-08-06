import type { Column } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';

import { z } from 'zod';

import { useCallback, type JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';

import { Button } from '@/components/ui/button';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

export interface ITableHeader<T> {
  column: Column<T>;
  sortable?: boolean;
  intlKey: MessagesKey;
  tooltipId?: MessagesKey;
}

const sortingMethods = ['asc', 'desc', 'false'] as const;
const DEFAULT_SORTING = 'false';
const zSortingEnum = z.enum(sortingMethods);
const zSortingMethod = zSortingEnum.catch(DEFAULT_SORTING);

const arrowClassName = 'ml-1 h-4 w-4 shrink-0';
const sortedArrow = {
  asc: <ArrowUp className={arrowClassName} />,
  desc: <ArrowDown className={arrowClassName} />,
  false: <ArrowUpDown className={arrowClassName} color="gray" />,
};

export const TableHeader = <T,>({
  column,
  sortable = true,
  intlKey,
  tooltipId,
}: ITableHeader<T>): JSX.Element => {
  const headerSort = useCallback(() => {
    if (sortable) {
      if (column.getIsSorted() === 'asc') {
        column.toggleSorting(true);
      } else if (column.getIsSorted() === 'desc') {
        column.clearSorting();
      } else {
        column.toggleSorting(false);
      }
    }
  }, [column, sortable]);

  return (
    <span className="flex min-w-0 items-center">
      <Button
        variant="ghost"
        className="max-w-full min-w-0 justify-start px-2"
        onClick={headerSort}
      >
        <span className="truncate">
          <FormattedMessage key={intlKey} id={intlKey} />
        </span>
        {sortable && sortedArrow[zSortingMethod.parse(column.getIsSorted())]}
      </Button>
      {tooltipId && (
        <TooltipIcon
          triggerClassName="ml-1 shrink-0"
          contentClassName="font-normal whitespace-pre-line"
          tooltipId={tooltipId}
        />
      )}
    </span>
  );
};
