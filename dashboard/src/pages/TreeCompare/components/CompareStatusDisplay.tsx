import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { GroupedTestStatus } from '@/components/Status/Status';

import type { CompareStatusCounts } from '@/types/tree/TreeCompare';

import { cn } from '@/lib/utils';

function formatSigned(n: number): string {
  if (n === 0) {
    return '0';
  }
  return n > 0 ? `+${n.toLocaleString()}` : n.toLocaleString();
}

export function StatusCountsDisplay({
  counts,
  hideInconclusive = false,
}: {
  counts: CompareStatusCounts;
  hideInconclusive?: boolean;
}): JSX.Element {
  return (
    <GroupedTestStatus
      preCalculatedGroupedStatus={{
        successCount: counts.pass,
        failedCount: counts.fail,
        inconclusiveCount: counts.inconclusive,
      }}
      hideInconclusive={hideInconclusive}
    />
  );
}

export function DeltaPair({
  passDelta,
  failDelta,
  className,
}: {
  passDelta: number;
  failDelta: number;
  className?: string;
}): JSX.Element {
  const passColor =
    passDelta === 0
      ? 'text-dim-gray'
      : passDelta > 0
        ? 'text-dark-green'
        : 'text-red';
  const failColor =
    failDelta === 0
      ? 'text-dim-gray'
      : failDelta > 0
        ? 'text-red'
        : 'text-dark-green';

  return (
    <div className={cn('flex flex-col gap-0.5 text-sm font-medium', className)}>
      <span className={passColor}>
        <FormattedMessage id="treeCompare.deltaPass" />:{' '}
        {formatSigned(passDelta)}
      </span>
      <span className={failColor}>
        <FormattedMessage id="treeCompare.deltaFail" />:{' '}
        {formatSigned(failDelta)}
      </span>
    </div>
  );
}

export function CountsWithLabel({
  label,
  counts,
}: {
  label: string;
  counts: CompareStatusCounts;
}): JSX.Element {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-medium tracking-wide text-dim-gray uppercase">
        {label}
      </span>
      <StatusCountsDisplay counts={counts} />
    </div>
  );
}
