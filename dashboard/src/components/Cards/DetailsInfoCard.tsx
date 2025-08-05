import type { JSX } from 'react';
import { useMemo } from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { DumbBaseTable } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';

import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';
import type { MessagesKey } from '@/locales/messages';

import BaseCard from './BaseCard';

interface DetailRow {
  title?: MessagesKey;
  value: ILinkWithIcon;
}

const columns: ColumnDef<DetailRow>[] = [
  {
    accessorKey: 'title',
    cell: ({ row }): JSX.Element => {
      return <FormattedMessage id={row.getValue('title')} />;
    },
  },
  {
    accessorKey: 'value',
    cell: ({ row }): JSX.Element => {
      return <LinkWithIcon {...row.getValue('value')} />;
    },
  },
];

export const DetailsInfoCard = ({
  cardTitle,
  data,
}: {
  cardTitle: MessagesKey;
  data: ILinkWithIcon[];
}): JSX.Element => {
  const sanitizedData: DetailRow[] = useMemo(
    () =>
      data.map(({ title, ...value }) => ({
        title,
        value: { ...value },
      })),
    [data],
  );

  const table = useReactTable({
    data: sanitizedData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const modelRows = table.getRowModel().rows;
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => {
            return (
              <TableCell
                key={cell.id}
                className={
                  cell.column.id === 'title'
                    ? 'text-center font-bold'
                    : 'break-all'
                }
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCell>
            );
          })}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows]);

  return (
    <BaseCard
      title={<FormattedMessage id={cardTitle} />}
      className="mb-0 gap-0"
    >
      <DumbBaseTable containerClassName="rounded-none border-0 border-x-0">
        <TableBody>{tableBody}</TableBody>
      </DumbBaseTable>
    </BaseCard>
  );
};
