import { PaginationState, Table } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { MdArrowBackIos, MdArrowForwardIos } from 'react-icons/md';

import { useMemo } from 'react';

import {
  AccordionItemBuilds,
  TestByCommitHash,
} from '@/types/tree/TreeDetails';

import { ItemsPerPageValues } from '@/utils/constants/general';

import { TPathTests } from '@/types/general';

import { ItemsPerPageSelector } from '../Table/TableInfo';
import { Button } from '../ui/button';

interface IPaginationInfo {
  table:
    | Table<TestByCommitHash>
    | Table<TPathTests>
    | Table<AccordionItemBuilds>;
  pagination: PaginationState;
  data: TestByCommitHash[] | TPathTests[] | AccordionItemBuilds[];
  label: 'builds' | 'boots' | 'tests';
}

export function PaginationInfo({
  table,
  pagination,
  data,
  label,
}: IPaginationInfo): JSX.Element {
  const buttonsClassName = 'text-blue font-bold';

  const pageIndex = table.getState().pagination.pageIndex;
  const startIndex = pageIndex * pagination.pageSize + 1;
  const endIndex =
    (pageIndex + 1) * pagination.pageSize < data.length
      ? (pageIndex + 1) * pagination.pageSize
      : data.length;

  const FormattedLabel = useMemo((): JSX.Element => {
    switch (label) {
      case 'builds':
        return (
          <FormattedMessage id="treeDetails.builds" defaultMessage="Builds" />
        );
      case 'boots':
        return (
          <FormattedMessage id="treeDetails.boots" defaultMessage="Boots" />
        );
      case 'tests':
        return (
          <FormattedMessage id="treeDetails.tests" defaultMessage="Tests" />
        );
    }
  }, [label]);

  return (
    <div className="flex flex-row justify-end gap-10 text-sm">
      <div className="flex flex-row items-center gap-2">
        <FormattedMessage id="table.showing" />
        <span className="font-bold">
          {startIndex} - {endIndex}
        </span>
        <FormattedMessage id="table.of" />
        <span className="font-bold">{data.length}</span>
        {FormattedLabel}
      </div>
      <ItemsPerPageSelector
        selected={table.getState().pagination.pageSize}
        onValueChange={table.setPageSize}
        values={ItemsPerPageValues}
      />
      <div className="flex flex-row items-center gap-2">
        <Button
          variant="outline"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          <MdArrowBackIos className={buttonsClassName} />
        </Button>
        <Button
          variant="outline"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          <MdArrowForwardIos className={buttonsClassName} />
        </Button>
      </div>
    </div>
  );
}
