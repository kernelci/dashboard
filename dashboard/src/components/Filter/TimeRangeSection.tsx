import { FormattedMessage } from 'react-intl';

import { Input } from '@/components/ui/input';

import { FilterTypeIcon } from './Drawer';

interface TimeRangeSection {
  title: string;
  subtitle: string;
  min: number | undefined;
  max: number | undefined;
  isGlobal?: boolean;
  onMinChange: (e: React.FormEvent<HTMLInputElement>) => void;
  onMaxChange: (e: React.FormEvent<HTMLInputElement>) => void;
}

const inputContainerClass = 'flex gap-x-4 items-center';
const inputClass = 'max-w-20';

const TimeRangeSection = ({
  title,
  subtitle,
  min,
  max,
  isGlobal = false,
  onMinChange,
  onMaxChange,
}: TimeRangeSection): JSX.Element => {
  return (
    <div className="flex flex-col gap-y-2 text-dimGray">
      <h3 className="mb-2 flex items-center gap-[0.4rem] text-xl font-semibold text-dimGray">
        <FilterTypeIcon type={isGlobal ? 'global' : 'tab'} />
        <span>{title}</span>
      </h3>
      <h4 className="text-s mb-6">{subtitle}</h4>
      <div className={inputContainerClass}>
        <span className="w-8">
          <FormattedMessage id="filter.min" />:
        </span>
        <Input
          className={inputClass}
          onChange={onMinChange}
          value={min || ''}
          min={0}
          type="number"
        />
      </div>

      <div className={inputContainerClass}>
        <span className="w-8">
          <FormattedMessage id="filter.max" />:
        </span>

        <Input
          className={inputClass}
          onChange={onMaxChange}
          value={max || ''}
          min={0}
          type="number"
        />
      </div>
    </div>
  );
};

export default TimeRangeSection;
