import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type JSX,
  type RefCallback,
} from 'react';

import {
  flexRender,
  useReactTable,
  type ColumnDef,
  type ColumnOrderState,
  type ColumnSizingState,
  type OnChangeFn,
  type RowData,
  type Table,
  type TableOptions,
  type VisibilityState,
} from '@tanstack/react-table';

import { ColumnsMenu } from '@/components/Table/ColumnsMenu';
import { LayoutTableHead } from '@/components/Table/LayoutTableHead';
import {
  distributeWidths,
  ensureRowHeadersFirst,
  getColumnId,
  getColumnLayoutMeta,
  moveColumnInOrder,
  normalizeColumns,
  type ColumnLayoutDefaults,
} from '@/utils/columnLayout';
import { TABLE_FRAME_BORDER_X } from '@/utils/constants/tables';

export { columnWidthStyle } from '@/utils/columnLayout';

type UseLayoutTableArgs<TData extends RowData> = {
  columns: ColumnDef<TData, unknown>[];
  defaults?: ColumnLayoutDefaults;
  initialColumnVisibility?: VisibilityState;
  /** Extra values that should force header cells to re-render (e.g. rowSelection). */
  extraHeaderDeps?: readonly unknown[];
} & Omit<
  TableOptions<TData>,
  | 'columns'
  | 'onColumnVisibilityChange'
  | 'onColumnOrderChange'
  | 'onColumnSizingChange'
  | 'columnResizeMode'
>;

type UseLayoutTableResult<TData extends RowData> = {
  table: Table<TData>;
  containerRef: RefCallback<HTMLDivElement>;
  columnWidths: Record<string, number>;
  tableWidth: number;
  onColumnSizesChange: (updates: Record<string, number | undefined>) => void;
  moveColumn: (columnId: string, direction: -1 | 1) => void;
  isColumnManuallySized: (columnId: string) => boolean;
  columnsMenu: JSX.Element;
  tableHeaders: JSX.Element[];
};

const hasOwn = (object: object, key: string): boolean =>
  Object.prototype.hasOwnProperty.call(object, key);

export const useLayoutTable = <TData extends RowData>({
  columns,
  defaults,
  initialColumnVisibility = {},
  extraHeaderDeps = [],
  state: callerState,
  ...tableOptions
}: UseLayoutTableArgs<TData>): UseLayoutTableResult<TData> => {
  const normalizedColumns = useMemo(
    () => normalizeColumns(columns, defaults),
    [columns, defaults],
  );

  const rowHeaderIds = useMemo(
    () =>
      normalizedColumns
        .filter(column => getColumnLayoutMeta(column.meta).isRowHeader)
        .map(column => getColumnId(column)),
    [normalizedColumns],
  );

  const defaultOrder = useMemo(() => {
    const ids = normalizedColumns.map(column => getColumnId(column));
    return ensureRowHeadersFirst(ids, rowHeaderIds);
  }, [normalizedColumns, rowHeaderIds]);

  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(
    initialColumnVisibility,
  );
  const [columnOrder, setColumnOrder] =
    useState<ColumnOrderState>(defaultOrder);
  const [columnSizing, setColumnSizing] = useState<ColumnSizingState>({});

  useEffect(() => {
    setColumnOrder(previous => {
      const known = new Set(defaultOrder);
      const kept = previous.filter(id => known.has(id));
      const missing = defaultOrder.filter(id => !kept.includes(id));
      return ensureRowHeadersFirst([...kept, ...missing], rowHeaderIds);
    });
  }, [defaultOrder, rowHeaderIds]);

  const [containerElement, setContainerElement] =
    useState<HTMLDivElement | null>(null);
  const containerRef = useCallback<RefCallback<HTMLDivElement>>(node => {
    setContainerElement(node);
  }, []);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    if (!containerElement) {
      setContainerWidth(0);
      return;
    }

    const observer = new ResizeObserver((entries): void => {
      const entry = entries[0];
      if (entry) {
        setContainerWidth(entry.contentRect.width);
      }
    });
    observer.observe(containerElement);
    setContainerWidth(containerElement.clientWidth);

    return (): void => {
      observer.disconnect();
    };
  }, [containerElement]);

  const onColumnOrderChange: OnChangeFn<ColumnOrderState> = useCallback(
    (updater): void => {
      setColumnOrder(previous => {
        const next =
          typeof updater === 'function' ? updater(previous) : updater;
        return ensureRowHeadersFirst(next, rowHeaderIds);
      });
    },
    [rowHeaderIds],
  );

  const moveColumn = useCallback(
    (columnId: string, direction: -1 | 1): void => {
      setColumnOrder(previous =>
        moveColumnInOrder(previous, columnId, direction, rowHeaderIds),
      );
    },
    [rowHeaderIds],
  );

  const isColumnManuallySized = useCallback(
    (columnId: string): boolean => hasOwn(columnSizing, columnId),
    [columnSizing],
  );

  const table = useReactTable({
    ...tableOptions,
    columns: normalizedColumns,
    onColumnVisibilityChange: setColumnVisibility,
    onColumnOrderChange,
    onColumnSizingChange: setColumnSizing,
    state: {
      ...callerState,
      columnVisibility,
      columnOrder,
      columnSizing,
    },
  });

  const visibleLeafColumns = table.getVisibleLeafColumns();

  const columnWidths = useMemo(() => {
    const visibleColumns = visibleLeafColumns.map(column => {
      const meta = getColumnLayoutMeta(column.columnDef.meta);
      return {
        id: column.id,
        minWidth: meta.minWidth ?? column.columnDef.minSize ?? 0,
        maxWidth:
          meta.maxWidth ?? column.columnDef.maxSize ?? Number.MAX_SAFE_INTEGER,
        widthWeight: meta.widthWeight ?? 1,
      };
    });

    // Leave room for the table frame border so content fits without a phantom scrollbar.
    const layoutWidth = Math.max(0, containerWidth - TABLE_FRAME_BORDER_X);

    if (layoutWidth <= 0 || visibleColumns.length === 0) {
      return Object.fromEntries(
        visibleColumns.map(column => [column.id, column.minWidth]),
      );
    }

    return distributeWidths(layoutWidth, visibleColumns, columnSizing);
  }, [visibleLeafColumns, containerWidth, columnSizing]);

  const tableWidth = useMemo(() => {
    return Object.values(columnWidths).reduce((sum, width) => sum + width, 0);
  }, [columnWidths]);

  const onColumnSizesChange = useCallback(
    (updates: Record<string, number | undefined>) => {
      setColumnSizing(previous => {
        let changed = false;
        const next = { ...previous };
        for (const [columnId, width] of Object.entries(updates)) {
          if (width === undefined) {
            if (hasOwn(next, columnId)) {
              delete next[columnId];
              changed = true;
            }
          } else if (next[columnId] !== width) {
            next[columnId] = width;
            changed = true;
          }
        }
        return changed ? next : previous;
      });
    },
    [],
  );

  const sorting = table.getState().sorting;
  const groupHeaders = table.getHeaderGroups()[0]?.headers ?? [];

  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map((header, index) => {
      const meta = getColumnLayoutMeta(header.column.columnDef.meta);
      const nextHeader = groupHeaders[index + 1];
      const nextMeta = nextHeader
        ? getColumnLayoutMeta(nextHeader.column.columnDef.meta)
        : undefined;

      return (
        <LayoutTableHead
          key={header.id}
          header={header}
          width={columnWidths[header.column.id]}
          minWidth={meta.minWidth ?? header.column.columnDef.minSize ?? 0}
          isManuallySized={isColumnManuallySized(header.column.id)}
          isFirstVisible={index === 0}
          isLastVisible={index === groupHeaders.length - 1}
          nextColumn={
            nextHeader
              ? {
                  id: nextHeader.column.id,
                  width:
                    columnWidths[nextHeader.column.id] ?? nextHeader.getSize(),
                  minWidth:
                    nextMeta?.minWidth ??
                    nextHeader.column.columnDef.minSize ??
                    0,
                }
              : undefined
          }
          onColumnSizesChange={onColumnSizesChange}
        >
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </LayoutTableHead>
      );
    });
    // sorting / extraHeaderDeps: force header re-render when table UI state
    // changes without producing new header object identities.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional
  }, [
    groupHeaders,
    sorting,
    columnWidths,
    isColumnManuallySized,
    onColumnSizesChange,
    extraHeaderDeps,
  ]);

  const columnsMenu = <ColumnsMenu table={table} moveColumn={moveColumn} />;

  return {
    table,
    containerRef,
    columnWidths,
    tableWidth,
    onColumnSizesChange,
    moveColumn,
    isColumnManuallySized,
    columnsMenu,
    tableHeaders,
  };
};
