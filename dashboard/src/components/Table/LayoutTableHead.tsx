import type { Header } from '@tanstack/react-table';
import { flexRender } from '@tanstack/react-table';
import type { JSX, ReactNode } from 'react';

import { TableHead } from '@/components/Table/BaseTable';
import {
  ColumnResizeHandle,
  type ResizeColumnSide,
} from '@/components/Table/ColumnResizeHandle';
import { ColumnResetWidthButton } from '@/components/Table/ColumnResetWidthButton';
import { columnWidthStyle } from '@/utils/columnLayout';

type LayoutTableHeadProps<TData> = {
  header: Header<TData, unknown>;
  width: number | undefined;
  minWidth: number;
  isManuallySized: boolean;
  isFirstVisible: boolean;
  isLastVisible: boolean;
  nextColumn?: ResizeColumnSide;
  onColumnSizesChange: (updates: Record<string, number | undefined>) => void;
  children?: ReactNode;
};

export const LayoutTableHead = <TData,>({
  header,
  width,
  minWidth,
  isManuallySized,
  isFirstVisible,
  isLastVisible,
  nextColumn,
  onColumnSizesChange,
  children,
}: LayoutTableHeadProps<TData>): JSX.Element => {
  const canResize = header.column.getCanResize();
  const thisColumn: ResizeColumnSide = {
    id: header.column.id,
    width: width ?? header.getSize(),
    minWidth,
  };

  return (
    <TableHead className="overflow-hidden" style={columnWidthStyle(width)}>
      <div className="flex min-w-0 items-center gap-0.5 pr-2">
        {isManuallySized && (
          <ColumnResetWidthButton
            onReset={() =>
              onColumnSizesChange({ [header.column.id]: undefined })
            }
          />
        )}
        <div className="min-w-0 flex-1 overflow-hidden">
          {children ??
            (header.isPlaceholder
              ? null
              : flexRender(
                  header.column.columnDef.header,
                  header.getContext(),
                ))}
        </div>
      </div>
      {canResize && isFirstVisible && (
        <ColumnResizeHandle
          edge="start"
          rightColumn={thisColumn}
          onSizingChange={onColumnSizesChange}
        />
      )}
      {canResize && (
        <ColumnResizeHandle
          edge="end"
          leftColumn={thisColumn}
          rightColumn={isLastVisible ? undefined : nextColumn}
          onSizingChange={onColumnSizesChange}
        />
      )}
    </TableHead>
  );
};
