import type { Column } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';

import { z } from 'zod';

import type { JSX } from 'react';

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
  return (
    <span className="flex">
      <Button
        variant="ghost"
        className="justify-start px-2"
        onClick={sortable ? column.getToggleSortingHandler() : undefined}
      >
        <FormattedMessage key={intlKey} id={intlKey} />

        {sortable && sortedArrow[zSortingMethod.parse(column.getIsSorted())]}
      </Button>
      {tooltipId && (
        <TooltipIcon
          triggerClassName="ml-2"
          contentClassName="font-normal whitespace-pre-line"
          tooltipId={tooltipId}
        />
      )}
    </span>
  );
};
