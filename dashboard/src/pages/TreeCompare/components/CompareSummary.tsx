import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { CompareEntitySummary } from '@/types/tree/TreeCompare';

import {
  CountsWithLabel,
  DeltaPair,
  StatusCountsDisplay,
} from './CompareStatusDisplay';

interface CompareSummaryCardProps {
  titleId: 'global.builds' | 'global.boots' | 'global.tests';
  summary: CompareEntitySummary;
}

function CompareSummaryCard({
  titleId,
  summary,
}: CompareSummaryCardProps): JSX.Element {
  const hasChange = summary.delta.pass !== 0 || summary.delta.fail !== 0;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-dim-gray">
        <FormattedMessage id={titleId} />
      </h3>

      <div className="mt-4 grid grid-cols-3 gap-3">
        <CountsWithLabel
          label="A"
          counts={summary.sideA}
        />
        <CountsWithLabel
          label="B"
          counts={summary.sideB}
        />
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium tracking-wide text-dim-gray uppercase">
            <FormattedMessage id="treeCompare.delta" />
          </span>
          <DeltaPair
            passDelta={summary.delta.pass}
            failDelta={summary.delta.fail}
          />
        </div>
      </div>

      <div className="border-medium-gray mt-4 flex items-center justify-between border-t pt-3">
        <div className="flex items-center gap-4 text-xs text-dim-gray">
          <span className="flex items-center gap-1.5">
            <FormattedMessage id="treeCompare.sideA" />:
            <StatusCountsDisplay counts={summary.sideA} hideInconclusive />
          </span>
          <span>→</span>
          <span className="flex items-center gap-1.5">
            <FormattedMessage id="treeCompare.sideB" />:
            <StatusCountsDisplay counts={summary.sideB} hideInconclusive />
          </span>
        </div>
        {hasChange && (
          <span className="bg-light-blue text-dark-blue rounded-full px-2 py-0.5 text-xs font-medium">
            <FormattedMessage id="treeCompare.changed" />
          </span>
        )}
      </div>
    </div>
  );
}

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
  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-dim-black">
        <FormattedMessage id="treeCompare.summaryTitle" />
      </h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <CompareSummaryCard titleId="global.builds" summary={builds} />
        <CompareSummaryCard titleId="global.boots" summary={boots} />
        <CompareSummaryCard titleId="global.tests" summary={tests} />
      </div>
    </section>
  );
}
