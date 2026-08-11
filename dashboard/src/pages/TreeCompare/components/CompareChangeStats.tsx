import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { CompareChangeFilter } from '@/types/tree/TreeCompare';

import type { MessagesKey } from '@/locales/messages';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { TooltipIcon } from '@/components/Icons/TooltipIcon';

import { toggleChangeFilter } from '@/utils/treeCompareDiff';

const FILTER_OPTIONS: {
  value: CompareChangeFilter;
  labelId: MessagesKey;
}[] = [
  { value: 'regression', labelId: 'treeCompare.change.regressions' },
  { value: 'fixed', labelId: 'treeCompare.change.fixed' },
  { value: 'newFailure', labelId: 'treeCompare.change.newFailures' },
  { value: 'stillFailing', labelId: 'treeCompare.change.stillFailing' },
  { value: 'newPass', labelId: 'treeCompare.change.newPasses' },
  { value: 'appeared', labelId: 'treeCompare.change.appeared' },
  { value: 'disappeared', labelId: 'treeCompare.change.disappeared' },
];

export function CompareChangeFilterBar({
  value,
  onChange,
}: {
  value: readonly CompareChangeFilter[];
  onChange: (value: CompareChangeFilter[]) => void;
}): JSX.Element {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-dim-gray flex items-center gap-1 text-sm">
        <FormattedMessage id="filter.tableFilter" />
        <TooltipIcon
          tooltipId="treeCompare.change.glossary"
          iconClassName="text-dim-gray size-4"
        />
      </span>
      <div className="flex flex-wrap gap-2">
        {FILTER_OPTIONS.map(option => {
          const selected = value.includes(option.value);
          return (
            <Button
              key={option.value}
              type="button"
              variant="outline"
              size="sm"
              aria-pressed={selected}
              className={cn(
                'rounded-full border-black',
                selected
                  ? 'bg-blue hover:bg-blue text-white hover:text-white'
                  : 'bg-white text-black',
              )}
              onClick={() => onChange(toggleChangeFilter(value, option.value))}
            >
              <FormattedMessage id={option.labelId} />
            </Button>
          );
        })}
      </div>
    </div>
  );
}
