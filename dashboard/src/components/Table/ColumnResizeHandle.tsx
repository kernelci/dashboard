import {
  useCallback,
  type JSX,
  type MouseEvent as ReactMouseEvent,
} from 'react';
import { useIntl } from 'react-intl';

import { cn } from '@/lib/utils';
import { resizeAdjacentColumns, resizeOuterColumn } from '@/utils/columnLayout';

export type ResizeColumnSide = {
  id: string;
  width: number;
  minWidth: number;
};

type ColumnResizeHandleProps = {
  /** Which edge of the header this handle sits on. */
  edge: 'start' | 'end';
  /**
   * Column immediately left of the handle (for `end` edge: this header;
   * for outer `start` on the first header: omitted).
   */
  leftColumn?: ResizeColumnSide;
  /**
   * Column immediately right of the handle (for interior `end` edges: next header;
   * for outer `end` on the last header: omitted; for `start` on first: this header).
   */
  rightColumn?: ResizeColumnSide;
  onSizingChange: (updates: Record<string, number>) => void;
};

/**
 * Column resize handle.
 * - Interior (both neighbors): moves width between left and right; table width fixed.
 * - Outer edge (one neighbor): resizes that column only; table width can change.
 * Manual resize is not limited by maxWidth.
 */
export const ColumnResizeHandle = ({
  edge,
  leftColumn,
  rightColumn,
  onSizingChange,
}: ColumnResizeHandleProps): JSX.Element => {
  const intl = useIntl();

  const onMouseDown = useCallback(
    (event: ReactMouseEvent) => {
      event.preventDefault();
      event.stopPropagation();

      const startX = event.clientX;
      const leftStart = leftColumn;
      const rightStart = rightColumn;

      const onMouseMove = (moveEvent: MouseEvent): void => {
        const delta = moveEvent.clientX - startX;

        if (leftStart && rightStart) {
          const { leftWidth, rightWidth } = resizeAdjacentColumns(
            { startWidth: leftStart.width, minWidth: leftStart.minWidth },
            { startWidth: rightStart.width, minWidth: rightStart.minWidth },
            delta,
          );
          onSizingChange({
            [leftStart.id]: leftWidth,
            [rightStart.id]: rightWidth,
          });
          return;
        }

        if (leftStart && !rightStart) {
          // Outer right edge: grow/shrink the last column.
          onSizingChange({
            [leftStart.id]: resizeOuterColumn(
              leftStart.width,
              leftStart.minWidth,
              delta,
            ),
          });
          return;
        }

        if (rightStart && !leftStart) {
          // Outer left edge: drag left grows the first column.
          onSizingChange({
            [rightStart.id]: resizeOuterColumn(
              rightStart.width,
              rightStart.minWidth,
              -delta,
            ),
          });
        }
      };

      const onMouseUp = (): void => {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    },
    [leftColumn, rightColumn, onSizingChange],
  );

  return (
    <div
      role="separator"
      aria-orientation="vertical"
      aria-label={intl.formatMessage({ id: 'table.resizeColumn' })}
      onMouseDown={onMouseDown}
      className={cn(
        'absolute top-0 z-10 flex h-full w-2 cursor-col-resize touch-none items-center justify-center select-none',
        edge === 'start' ? 'left-0' : 'right-0',
        'after:bg-dark-gray after:block after:h-1/2 after:w-0.5 after:rounded-full after:opacity-60',
        'hover:after:bg-slate-700 hover:after:opacity-100',
      )}
    />
  );
};
