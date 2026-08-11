import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';
import type { CompareEntitySummary } from '@/types/tree/TreeCompare';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { cn } from '@/lib/utils';

type MatrixRowId = 'fixes' | 'regressions' | 'pass' | 'fail' | 'other';

type MatrixRow = {
  id: MatrixRowId;
  labelId: MessagesKey;
  valueClassName: string;
  striped?: boolean;
  getValue: (summary: CompareEntitySummary) => number;
};

const MATRIX_ROWS: MatrixRow[] = [
  {
    id: 'fixes',
    labelId: 'treeCompare.matrix.fixes',
    valueClassName: 'text-dark-green',
    getValue: s => s.changes.fixed,
  },
  {
    id: 'regressions',
    labelId: 'treeCompare.matrix.regressions',
    valueClassName: 'text-red',
    striped: true,
    getValue: s => s.changes.regression,
  },
  {
    id: 'pass',
    labelId: 'treeCompare.matrix.pass',
    valueClassName: 'text-dark-green',
    getValue: s => s.sideB.pass,
  },
  {
    id: 'fail',
    labelId: 'treeCompare.matrix.fail',
    valueClassName: 'text-red',
    striped: true,
    getValue: s => s.sideB.fail,
  },
  {
    id: 'other',
    labelId: 'treeCompare.matrix.other',
    valueClassName: 'text-dim-gray',
    getValue: s => s.sideB.inconclusive,
  },
];

const ENTITY_COLUMNS: {
  key: 'builds' | 'boots' | 'tests';
  labelId: MessagesKey;
}[] = [
  { key: 'builds', labelId: 'treeCompare.matrix.builds' },
  { key: 'boots', labelId: 'treeCompare.matrix.boots' },
  { key: 'tests', labelId: 'treeCompare.matrix.tests' },
];

interface CompareSummaryProps {
  builds: CompareEntitySummary;
  boots: CompareEntitySummary;
  tests: CompareEntitySummary;
}

export function CompareSummary({
  builds,
  boots,
  tests,
}: CompareSummaryProps): JSX.Element {
  const summaries = { builds, boots, tests };

  return (
    <section>
      <h2 className="text-dim-black mb-4 text-lg font-semibold">
        <FormattedMessage id="treeCompare.summaryTitle" />
      </h2>
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <Table containerClassName="rounded-none border-0">
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-40" />
              {ENTITY_COLUMNS.map(column => (
                <TableHead
                  key={column.key}
                  className="text-dim-gray text-right text-[13px] font-semibold tracking-wide"
                >
                  <FormattedMessage id={column.labelId} />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {MATRIX_ROWS.map(row => (
              <TableRow
                key={row.id}
                className={cn(
                  'hover:bg-transparent',
                  row.striped && 'bg-light-gray hover:bg-light-gray',
                )}
              >
                <TableCell className="text-dim-gray w-40 text-right font-medium">
                  <FormattedMessage id={row.labelId} />
                </TableCell>
                {ENTITY_COLUMNS.map(column => (
                  <TableCell
                    key={column.key}
                    className={cn(
                      'text-right font-mono text-[15px] font-medium',
                      row.valueClassName,
                    )}
                  >
                    {row.getValue(summaries[column.key]).toLocaleString()}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </section>
  );
}
