import type {
  ColumnDef,
  ColumnSizingState,
  RowData,
} from '@tanstack/react-table';

import type { ListingTableColumnMeta } from '@/types/table';
import {
  DEFAULT_COLUMN_MAX_WIDTH,
  DEFAULT_COLUMN_MIN_WIDTH,
  DEFAULT_COLUMN_WIDTH_WEIGHT,
} from '@/utils/constants/tables';

export type ColumnLayoutDefaults = {
  minWidth?: number;
  maxWidth?: number;
  widthWeight?: number;
};

export type ColumnWidthInput = {
  id: string;
  minWidth: number;
  maxWidth: number;
  widthWeight: number;
};

export const getColumnId = <TData extends RowData>(
  column: ColumnDef<TData, unknown>,
): string => {
  if (column.id !== undefined) {
    return column.id;
  }
  if ('accessorKey' in column && column.accessorKey !== undefined) {
    // TanStack replaces '.' with '_' when deriving ids from accessorKey.
    return String(column.accessorKey).replace(/\./g, '_');
  }
  throw new Error('Column must have an id or accessorKey');
};

export const getColumnLayoutMeta = (meta: unknown): ListingTableColumnMeta => {
  return (meta ?? {}) as ListingTableColumnMeta;
};

export const normalizeColumns = <TData extends RowData>(
  columns: ColumnDef<TData, unknown>[],
  defaults: ColumnLayoutDefaults = {},
): ColumnDef<TData, unknown>[] => {
  const defaultMin = defaults.minWidth ?? DEFAULT_COLUMN_MIN_WIDTH;
  const defaultMax = defaults.maxWidth ?? DEFAULT_COLUMN_MAX_WIDTH;
  const defaultWeight = defaults.widthWeight ?? DEFAULT_COLUMN_WIDTH_WEIGHT;

  return columns.map(column => {
    const meta = getColumnLayoutMeta(column.meta);
    const minWidth = meta.minWidth ?? defaultMin;
    const maxWidth = meta.maxWidth ?? defaultMax;
    const widthWeight = meta.widthWeight ?? defaultWeight;

    return {
      ...column,
      ...(meta.isRowHeader ? { enableHiding: false } : {}),
      minSize: minWidth,
      maxSize: maxWidth,
      size: column.size ?? minWidth,
      meta: {
        ...meta,
        minWidth,
        maxWidth,
        widthWeight,
      },
    };
  });
};

/**
 * Assign pixel widths for visible columns.
 * Columns present in `columnSizing` are manual (user-resized); others share remaining space.
 */
export const distributeWidths = (
  containerWidth: number,
  columns: ColumnWidthInput[],
  columnSizing: ColumnSizingState,
): Record<string, number> => {
  const widths: Record<string, number> = {};
  const dynamic: ColumnWidthInput[] = [];
  let manualSum = 0;

  for (const column of columns) {
    if (Object.prototype.hasOwnProperty.call(columnSizing, column.id)) {
      const fixed = columnSizing[column.id];
      widths[column.id] = fixed;
      manualSum += fixed;
    } else {
      dynamic.push(column);
    }
  }

  if (dynamic.length === 0) {
    return widths;
  }

  const remaining = containerWidth - manualSum;
  const minSum = dynamic.reduce((sum, column) => sum + column.minWidth, 0);
  const maxSum = dynamic.reduce((sum, column) => sum + column.maxWidth, 0);

  if (remaining >= maxSum) {
    for (const column of dynamic) {
      widths[column.id] = column.maxWidth;
    }
    return widths;
  }

  if (remaining <= minSum) {
    for (const column of dynamic) {
      widths[column.id] = column.minWidth;
    }
    return widths;
  }

  Object.assign(widths, allocateByWeight(remaining, dynamic));
  return widths;
};

const allocateByWeight = (
  budget: number,
  columns: ColumnWidthInput[],
): Record<string, number> => {
  const widths: Record<string, number> = {};
  const flexible = new Map(columns.map(column => [column.id, column]));
  let remainingBudget = budget;

  // Clamp columns that hit min/max under proportional share; repeat until stable.
  let guard = columns.length + 1;
  while (flexible.size > 0 && guard > 0) {
    guard -= 1;
    const weightSum = [...flexible.values()].reduce(
      (sum, column) => sum + column.widthWeight,
      0,
    );
    const shares = new Map<string, number>();
    for (const column of flexible.values()) {
      shares.set(column.id, remainingBudget * (column.widthWeight / weightSum));
    }

    let clamped = false;
    for (const column of [...flexible.values()]) {
      const share = shares.get(column.id) ?? 0;
      if (share <= column.minWidth) {
        widths[column.id] = column.minWidth;
        remainingBudget -= column.minWidth;
        flexible.delete(column.id);
        clamped = true;
      } else if (share >= column.maxWidth) {
        widths[column.id] = column.maxWidth;
        remainingBudget -= column.maxWidth;
        flexible.delete(column.id);
        clamped = true;
      }
    }

    if (clamped) {
      continue;
    }

    const ids = [...flexible.keys()];
    let assigned = 0;
    ids.forEach((id, index) => {
      const column = flexible.get(id);
      if (!column) {
        return;
      }
      if (index === ids.length - 1) {
        widths[id] = Math.round(remainingBudget - assigned);
      } else {
        const width = Math.round(
          remainingBudget * (column.widthWeight / weightSum),
        );
        widths[id] = width;
        assigned += width;
      }
      flexible.delete(id);
    });
  }

  return widths;
};

export const ensureRowHeadersFirst = (
  order: string[],
  rowHeaderIds: readonly string[],
): string[] => {
  if (rowHeaderIds.length === 0) {
    return order;
  }
  const headerSet = new Set(rowHeaderIds);
  const headers = rowHeaderIds.filter(id => order.includes(id));
  const rest = order.filter(id => !headerSet.has(id));
  return [...headers, ...rest];
};

export const moveColumnInOrder = (
  order: string[],
  columnId: string,
  direction: -1 | 1,
  rowHeaderIds: readonly string[],
): string[] => {
  const headerSet = new Set(rowHeaderIds);
  if (headerSet.has(columnId)) {
    return order;
  }

  const headers = order.filter(id => headerSet.has(id));
  const rest = order.filter(id => !headerSet.has(id));
  const index = rest.indexOf(columnId);
  const nextIndex = index + direction;
  if (index < 0 || nextIndex < 0 || nextIndex >= rest.length) {
    return order;
  }

  const nextRest = [...rest];
  [nextRest[index], nextRest[nextIndex]] = [
    nextRest[nextIndex],
    nextRest[index],
  ];
  return [...headers, ...nextRest];
};

export const columnWidthStyle = (
  width: number | undefined,
): { width?: number; minWidth?: number; maxWidth?: number } => {
  if (width === undefined) {
    return {};
  }
  return { width, minWidth: width, maxWidth: width };
};

/**
 * Dual-column resize: move `delta` px from the right column to the left (or the reverse).
 * Keeps the pair's total width fixed and respects each column's minWidth only (no max).
 */
export const resizeAdjacentColumns = (
  left: { startWidth: number; minWidth: number },
  right: { startWidth: number; minWidth: number },
  delta: number,
): { leftWidth: number; rightWidth: number } => {
  const total = left.startWidth + right.startWidth;
  const leftMax = total - right.minWidth;
  const leftWidth = Math.min(
    leftMax,
    Math.max(left.minWidth, Math.round(left.startWidth + delta)),
  );
  return { leftWidth, rightWidth: total - leftWidth };
};

/** Single-column outer-edge resize; clamps to minWidth only (no max). */
export const resizeOuterColumn = (
  startWidth: number,
  minWidth: number,
  delta: number,
): number => Math.max(minWidth, Math.round(startWidth + delta));
