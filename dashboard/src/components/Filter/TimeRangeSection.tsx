import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { Input } from '@/components/ui/input';

import { FilterTypeIcon } from './Drawer';

interface TimeRangeSection {
  title: string;
  min: number | undefined;
  max: number | undefined;
  isGlobal?: boolean;
  onMinChange: (e: React.FormEvent<HTMLInputElement>) => void;
  onMaxChange: (e: React.FormEvent<HTMLInputElement>) => void;
}

const inputClass = 'h-8 max-w-20';

const TimeRangeSection = ({
  title,
  min,
  max,
  isGlobal = false,
  onMinChange,
  onMaxChange,
}: TimeRangeSection): JSX.Element => {
  return (
    <div className="text-dim-gray">
      <h3 className="text-dim-gray mb-2 flex items-center gap-[0.4rem] text-base font-semibold">
        <FilterTypeIcon type={isGlobal ? 'global' : 'tab'} />
        <span>{title}</span>
      </h3>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <label className="flex items-center gap-2">
          <span>
            <FormattedMessage id="filter.min" />:
          </span>
          <Input
            className={inputClass}
            onChange={onMinChange}
            value={min ?? ''}
            min={0}
            type="number"
          />
        </label>
        <label className="flex items-center gap-2">
          <span>
            <FormattedMessage id="filter.max" />:
          </span>
          <Input
            className={inputClass}
            onChange={onMaxChange}
            value={max ?? ''}
            min={0}
            type="number"
          />
        </label>
      </div>
    </div>
  );
};

export default TimeRangeSection;
