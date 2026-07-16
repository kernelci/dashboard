import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import type { CompareGroupRow } from '@/types/tree/TreeCompare';

import { cn } from '@/lib/utils';

import { DeltaPair, StatusCountsDisplay } from './CompareStatusDisplay';

interface CompareDeltaTableProps {
  rows: CompareGroupRow[];
  groupColumnLabelId: 'treeCompare.group.builds' | 'treeCompare.group.boots' | 'treeCompare.group.tests';
}

export function CompareDeltaTable({
  rows,
  groupColumnLabelId,
}: CompareDeltaTableProps): JSX.Element {
  const sortedRows = [...rows].sort((a, b) => {
    const aImpact = Math.abs(a.delta.pass) + Math.abs(a.delta.fail);
    const bImpact = Math.abs(b.delta.pass) + Math.abs(b.delta.fail);
    if (aImpact !== bImpact) {
      return bImpact - aImpact;
    }
    return a.label.localeCompare(b.label);
  });

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <Table>
        <TableHeader>
          <TableRow className="bg-light-gray hover:bg-light-gray">
            <TableHead className="w-[28%] font-semibold">
              <FormattedMessage id={groupColumnLabelId} />
            </TableHead>
            <TableHead className="text-center font-semibold">
              <FormattedMessage id="treeCompare.sideA" />
            </TableHead>
            <TableHead className="w-8 text-center" />
            <TableHead className="text-center font-semibold">
              <FormattedMessage id="treeCompare.sideB" />
            </TableHead>
            <TableHead className="text-right font-semibold">
              <FormattedMessage id="treeCompare.delta" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedRows.map(row => {
            const hasChange = row.delta.pass !== 0 || row.delta.fail !== 0;

            return (
              <TableRow
                key={row.id}
                className={cn(hasChange && 'bg-light-blue/30')}
              >
                <TableCell className="font-medium text-dim-black">
                  {row.label}
                </TableCell>
                <TableCell>
                  <div className="flex justify-center">
                    <StatusCountsDisplay counts={row.sideA} />
                  </div>
                </TableCell>
                <TableCell className="text-center text-dim-gray">→</TableCell>
                <TableCell>
                  <div className="flex justify-center">
                    <StatusCountsDisplay counts={row.sideB} />
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex justify-end">
                    <DeltaPair
                      passDelta={row.delta.pass}
                      failDelta={row.delta.fail}
                    />
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
