import type { Column } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { LiaQuestionCircle } from 'react-icons/lia';

import { z } from 'zod';

import { useCallback, type JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';
import { formattedBreakLineValue } from '@/locales/messages';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { Button } from '@/components/ui/button';

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

const arrowClassName = 'ml-1 h-4 w-4';
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
    <span className="flex">
      <Button
        variant="ghost"
        className="justify-start px-2"
        onClick={headerSort}
      >
        <FormattedMessage key={intlKey} id={intlKey} />

        {sortable && sortedArrow[zSortingMethod.parse(column.getIsSorted())]}
      </Button>
      {tooltipId && (
        <Tooltip>
          <TooltipTrigger className="ml-2">
            <LiaQuestionCircle />
          </TooltipTrigger>
          <TooltipContent className="font-normal whitespace-pre-line">
            <FormattedMessage id={tooltipId} values={formattedBreakLineValue} />
          </TooltipContent>
        </Tooltip>
      )}
    </span>
  );
};
