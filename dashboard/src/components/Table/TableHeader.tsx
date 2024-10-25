import { Column } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';
import { LiaQuestionCircle } from 'react-icons/lia';

import { z } from 'zod';

import { useCallback } from 'react';

import {
  AccordionItemBuilds,
  TestByCommitHash,
} from '@/types/tree/TreeDetails';
import { TIndividualTest, TPathTests } from '@/types/general';
import { formattedBreakLineValue, MessagesKey } from '@/locales/messages';

import { Button } from '../ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '../Tooltip';

interface ITableHeader {
  column:
    | Column<TIndividualTest>
    | Column<TestByCommitHash>
    | Column<TPathTests>
    | Column<AccordionItemBuilds>;
  sortable: boolean;
  intlKey: MessagesKey;
  intlDefaultMessage: string;
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

export function TableHeader({
  column,
  sortable,
  intlKey,
  intlDefaultMessage,
  tooltipId,
}: ITableHeader): JSX.Element {
  const headerSort = useCallback(() => {
    if (sortable)
      if (column.getIsSorted() === 'asc') {
        column.toggleSorting(true);
      } else if (column.getIsSorted() === 'desc') {
        column.clearSorting();
      } else {
        column.toggleSorting(false);
      }
  }, [column, sortable]);

  return (
    <span className="flex">
      <Button
        variant="ghost"
        className="justify-start px-2"
        onClick={headerSort}
      >
        <FormattedMessage
          key={intlKey}
          id={intlKey}
          defaultMessage={intlDefaultMessage}
        ></FormattedMessage>

        {sortable && sortedArrow[zSortingMethod.parse(column.getIsSorted())]}
      </Button>
      {tooltipId && (
        <Tooltip>
          <TooltipTrigger>
            <LiaQuestionCircle />
          </TooltipTrigger>
          <TooltipContent className="font-normal">
            <FormattedMessage id={tooltipId} values={formattedBreakLineValue} />
          </TooltipContent>
        </Tooltip>
      )}
    </span>
  );
}
