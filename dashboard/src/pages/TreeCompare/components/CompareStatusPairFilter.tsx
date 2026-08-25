import type { JSX } from 'react';
import { useState } from 'react';

import { Plus, X } from 'lucide-react';
import { FormattedMessage, useIntl } from 'react-intl';

import {
  compareItemStatuses,
  type CompareChangeType,
  type CompareItemStatus,
  type CompareStatusPair,
} from '@/types/tree/TreeCompare';
import type { MessagesKey } from '@/locales/messages';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import {
  changeTypeIsSelected,
  toggleChangeTypePairs,
} from '@/utils/treeCompareDiff';

export type { CompareStatusPair };

const QUICK_FILTERS: {
  value: CompareChangeType;
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

export function CompareStatusSelect({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value?: CompareItemStatus;
  onChange: (value: CompareItemStatus) => void;
}): JSX.Element {
  return (
    <div className="flex min-w-36 flex-1 flex-col gap-1">
      <label htmlFor={id} className="text-dim-gray text-xs font-medium">
        {label}
      </label>
      <Select
        value={value}
        onValueChange={selected => onChange(selected as CompareItemStatus)}
      >
        <SelectTrigger id={id}>
          <SelectValue
            placeholder={
              <FormattedMessage id="treeCompare.statusPairFilter.select" />
            }
          />
        </SelectTrigger>
        <SelectContent>
          {compareItemStatuses.map(status => (
            <SelectItem key={status} value={status}>
              {status}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

export function CompareStatusPairChip({
  pair,
  onRemove,
}: {
  pair: CompareStatusPair;
  onRemove: () => void;
}): JSX.Element {
  const { formatMessage } = useIntl();

  return (
    <span className="bg-light-blue text-dark-blue inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold">
      {pair.from} → {pair.to}
      <button
        type="button"
        className="hover:bg-medium-light-blue ml-0.5 rounded-full p-0.5"
        onClick={onRemove}
        aria-label={formatMessage(
          { id: 'treeCompare.statusPairFilter.remove' },
          { from: pair.from, to: pair.to },
        )}
      >
        <X className="size-3" />
      </button>
    </span>
  );
}

export function CompareStatusPairFilter({
  value,
  onChange,
}: {
  value: readonly CompareStatusPair[];
  onChange: (value: CompareStatusPair[]) => void;
}): JSX.Element {
  const { formatMessage } = useIntl();
  const [from, setFrom] = useState<CompareItemStatus>();
  const [to, setTo] = useState<CompareItemStatus>();
  const isDuplicate = value.some(pair => pair.from === from && pair.to === to);
  const canAdd = from !== undefined && to !== undefined && !isDuplicate;

  const addPair = (): void => {
    if (!canAdd) {
      return;
    }
    onChange([...value, { from, to }]);
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="text-dim-gray flex items-center gap-1 text-sm">
        <FormattedMessage id="filter.tableFilter" />
        <TooltipIcon
          tooltipId="treeCompare.change.glossary"
          iconClassName="text-dim-gray size-4"
        />
        <TooltipIcon
          tooltipId="treeCompare.statusPairFilter.glossary"
          iconClassName="text-dim-gray size-4"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {QUICK_FILTERS.map(option => {
          const selected = changeTypeIsSelected(value, option.value);
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
              onClick={() =>
                onChange(toggleChangeTypePairs(value, option.value))
              }
            >
              <FormattedMessage id={option.labelId} />
            </Button>
          );
        })}
      </div>

      <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-end">
        <CompareStatusSelect
          id="compare-status-from"
          label={formatMessage({ id: 'treeCompare.statusPairFilter.from' })}
          value={from}
          onChange={setFrom}
        />
        <CompareStatusSelect
          id="compare-status-to"
          label={formatMessage({ id: 'treeCompare.statusPairFilter.to' })}
          value={to}
          onChange={setTo}
        />
        <Button
          type="button"
          variant="outline"
          className="shrink-0 gap-2"
          disabled={!canAdd}
          onClick={addPair}
        >
          <Plus className="size-4" />
          <FormattedMessage id="treeCompare.statusPairFilter.add" />
        </Button>
      </div>

      {value.length > 0 && (
        <div
          className="flex flex-wrap gap-2"
          aria-label={formatMessage({
            id: 'treeCompare.statusPairFilter.active',
          })}
        >
          {value.map(pair => (
            <CompareStatusPairChip
              key={`${pair.from}-${pair.to}`}
              pair={pair}
              onRemove={() =>
                onChange(
                  value.filter(
                    item => item.from !== pair.from || item.to !== pair.to,
                  ),
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
