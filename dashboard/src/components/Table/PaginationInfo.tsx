import type { Table } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { MdArrowBackIos, MdArrowForwardIos } from 'react-icons/md';

import { useMemo } from 'react';

import type {
  AccordionItemBuilds,
  TestByCommitHash,
} from '@/types/tree/TreeDetails';

import { ItemsPerPageValues } from '@/utils/constants/general';

import type { TPathTests } from '@/types/general';

import type { MessagesKey } from '@/locales/messages';

import type { TreeTableBody } from '@/types/tree/Tree';

import type { HardwareTableItem } from '@/types/hardware';

import { Button } from '@/components/ui/button';
import type { Trees } from '@/types/hardware/hardwareDetails';

import { ItemsPerPageSelector } from './TableInfo';

interface IPaginationInfo {
  //TODO Use Generic
  table:
    | Table<TestByCommitHash>
    | Table<TPathTests>
    | Table<AccordionItemBuilds>
    | Table<TreeTableBody>
    | Table<HardwareTableItem>
    | Table<Trees>;
  intlLabel: MessagesKey;
}

export function PaginationInfo({
  table,
  intlLabel,
}: IPaginationInfo): JSX.Element {
  const buttonsClassName = 'text-blue font-bold';

  const filteredRowModel = table.getFilteredRowModel();
  const countData = useMemo(
    () => filteredRowModel.rows.length,
    [filteredRowModel],
  );

  const pagination = table.getState().pagination;
  const pageIndex = pagination.pageIndex;
  const pageSize = pagination.pageSize;
  const startIndex = countData > 0 ? pageIndex * pageSize + 1 : 0;
  const endIndex = Math.min((pageIndex + 1) * pageSize, countData);

  return (
    <div className="flex flex-row justify-end gap-4 text-sm">
      <div className="flex flex-row items-center gap-2">
        <FormattedMessage id="table.showing" />
        <span className="font-bold">
          {startIndex} - {endIndex}
        </span>
        <FormattedMessage id="table.of" />
        <span className="font-bold">{countData}</span>
        <FormattedMessage id={intlLabel} defaultMessage="Trees" />
      </div>
      <ItemsPerPageSelector
        selected={table.getState().pagination.pageSize}
        onValueChange={table.setPageSize}
        values={ItemsPerPageValues}
      />
      <div className="flex flex-row items-center gap-2">
        <Button
          variant="outline"
          onClick={table.previousPage}
          disabled={!table.getCanPreviousPage()}
        >
          <MdArrowBackIos className={buttonsClassName} />
        </Button>
        <Button
          variant="outline"
          onClick={table.nextPage}
          disabled={!table.getCanNextPage()}
        >
          <MdArrowForwardIos className={buttonsClassName} />
        </Button>
      </div>
    </div>
  );
}
