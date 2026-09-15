import type { ChangeEvent, JSX } from 'react';

import { useIntl } from 'react-intl';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { TableCell } from '@/components/ui/table';

import type { CompareItemStatus } from '@/types/tree/TreeCompare';

import { CompareStatusChip } from './CompareChangeDisplay';

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
