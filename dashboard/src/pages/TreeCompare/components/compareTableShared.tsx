import { useCallback, useState, type ChangeEvent, type JSX } from 'react';

import { useIntl } from 'react-intl';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { TableCell } from '@/components/ui/table';

import type { LogType } from '@/hooks/useLogData';
import type {
  CompareFailureRow,
  CompareItemStatus,
} from '@/types/tree/TreeCompare';
import { compareRowNav } from '@/utils/treeCompareDiff';

import { CompareStatusChip } from './CompareChangeDisplay';
import {
  CompareDetailSheet,
  compareRowToDetailItem,
} from './CompareDetailSheet';

export function useCompareSheet(
  visibleRows: CompareFailureRow[],
  logType: LogType,
): {
  selectedId: string | null;
  openRow: (id: string) => void;
  sheet: JSX.Element;
} {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const nav = compareRowNav(visibleRows, selectedId);

  const openRow = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  const closeSheet = useCallback((open: boolean) => {
    if (!open) {
      setSelectedId(null);
    }
  }, []);

  const goToPrevious = useCallback(() => {
    if (nav.previousId) {
      setSelectedId(nav.previousId);
    }
  }, [nav.previousId]);

  const goToNext = useCallback(() => {
    if (nav.nextId) {
      setSelectedId(nav.nextId);
    }
  }, [nav.nextId]);

  return {
    selectedId,
    openRow,
    sheet: (
      <CompareDetailSheet
        open={nav.row !== null}
        item={nav.row ? compareRowToDetailItem(nav.row) : null}
        logType={logType}
        onOpenChange={closeSheet}
        onPrevious={goToPrevious}
        onNext={goToNext}
        hasPrevious={nav.hasPrevious}
        hasNext={nav.hasNext}
      />
    ),
  };
}

export function rowMatchesSearch(values: unknown[], query: string): boolean {
  if (!query) {
    return true;
  }
  const needle = query.toLowerCase();
  return values.some(value =>
    String(value ?? '')
      .toLowerCase()
      .includes(needle),
  );
}

export function CompareTableSearch({
  onSearchChange,
}: {
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
}): JSX.Element {
  const { formatMessage } = useIntl();

  // mt keeps the input clear of the sticky tabs header, which overlaps its top border.
  return (
    <div className="mt-2 mb-4 flex flex-col items-center gap-4 sm:flex-row sm:justify-end">
      <DebounceInput
        debouncedSideEffect={onSearchChange}
        className="w-9/10 sm:w-50"
        type="text"
        placeholder={formatMessage({ id: 'global.search' })}
      />
    </div>
  );
}

export function CompareSideCells({
  sideA,
  sideB,
}: {
  sideA: CompareItemStatus;
  sideB: CompareItemStatus;
}): JSX.Element {
  return (
    <>
      <TableCell>
        <div className="flex justify-center">
          <CompareStatusChip status={sideA} />
        </div>
      </TableCell>
      <TableCell className="text-dim-gray text-center">→</TableCell>
      <TableCell>
        <div className="flex justify-center">
          <CompareStatusChip status={sideB} />
        </div>
      </TableCell>
    </>
  );
}
