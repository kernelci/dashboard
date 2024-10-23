import { Column } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';

import { LiaQuestionCircle } from 'react-icons/lia';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { Button } from '@/components/ui/button';

import { TIndividualTest, TPathTests } from '@/types/general';
import { formattedBreakLineValue, MessagesKey } from '@/locales/messages';
import {
  AccordionItemBuilds,
  TestByCommitHash,
} from '@/types/tree/TreeDetails';

interface INewTableHeader {
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

export function NewTableHeader({
  column,
  sortable,
  intlKey,
  intlDefaultMessage,
  tooltipId,
}: INewTableHeader): JSX.Element {
  return (
    <span className="flex">
      <Button
        variant="ghost"
        className="justify-start px-2"
        onClick={() => {
          if (sortable)
            if (column.getIsSorted() === 'asc') {
              column.toggleSorting(true);
            } else if (column.getIsSorted() === 'desc') {
              column.clearSorting();
            } else {
              column.toggleSorting(false);
            }
        }}
      >
        <FormattedMessage
          key={intlKey}
          id={intlKey}
          defaultMessage={intlDefaultMessage}
        ></FormattedMessage>

        {(column.getIsSorted() as string) === 'asc' ? (
          <ArrowUp className="ml-1 h-4 w-4" />
        ) : (column.getIsSorted() as string) === 'desc' ? (
          <ArrowDown className="ml-1 h-4 w-4" />
        ) : (
          <ArrowUpDown className="ml-1 h-4 w-4" color="gray" />
        )}
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
