import cls from 'classnames';

import { useCallback, useMemo, type JSX } from 'react';

import { useIntl, type IntlShape, type MessageDescriptor } from 'react-intl';
import { Check, ChevronsUpDown } from 'lucide-react';
import { IoClose } from 'react-icons/io5';

import type { TFilterObjectsKeys } from '@/types/general';

import Checkbox from '@/components/Checkbox/Checkbox';
import { Badge } from '@/components/ui/badge';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverAnchor,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import { OptionFilters } from '@/types/filters';

import { FilterTypeIcon } from './Drawer';

const CHIP_LIST_LIMIT = 8;

type TOnClickItem = (value: string) => void;

type TItems = { [key: string]: boolean };

interface ICheckboxSectionItem {
  value: string;
  onClickItem: TOnClickItem;
  isSelected: boolean;
}

interface ICheckboxList {
  items: TItems;
  onClickItem: TOnClickItem;
  // Names the combobox trigger, which otherwise has only a chevron.
  title: string;
}

interface ICheckboxSubsection {
  items: TItems;
  title: string;
  onClickItem: TOnClickItem;
}

export interface ICheckboxSection {
  items?: TItems;
  title: string;
  subtitle?: string;
  isGlobal?: boolean;
  subsections?: ICheckboxSubsection[];
  onClickItem: TOnClickItem;
  className?: string;
  showIcon: boolean;
}

export interface ISectionItem {
  title: MessageDescriptor['id'];
  subtitle?: MessageDescriptor['id'];
  sectionKey: TFilterObjectsKeys;
  isGlobal?: boolean;
}

const checkboxLabel = (
  value: string,
  formatMessage: IntlShape['formatMessage'],
): string => {
  for (const page of Object.values(OptionFilters)) {
    if (value in page) {
      return formatMessage({ id: page[value].displayTextId });
    }
  }

  return value.split('__')[0] ?? '';
};

const CheckboxSectionItem = ({
  value,
  onClickItem,
  isSelected,
}: ICheckboxSectionItem): JSX.Element => {
  const { formatMessage } = useIntl();
  const handleOnToggle = useCallback(
    () => onClickItem(value),
    [value, onClickItem],
  );

  return (
    <Checkbox
      onToggle={handleOnToggle}
      text={checkboxLabel(value, formatMessage)}
      isChecked={isSelected}
    />
  );
};

const FilterMultiCombobox = ({
  items,
  onClickItem,
  title,
}: ICheckboxList): JSX.Element => {
  const { formatMessage } = useIntl();
  const keys = Object.keys(items);
  const selected = keys.filter(key => items[key]);
  const label = (value: string): string => checkboxLabel(value, formatMessage);

  return (
    <Popover>
      {/* The chips and Clear are buttons, so they sit beside the trigger
          instead of inside it. The anchor keeps the list the width of both. */}
      <PopoverAnchor asChild>
        <div className="border-dark-gray flex min-h-10 w-full max-w-xl items-center gap-2 rounded-md border bg-white px-3 py-2">
          <span className="flex max-h-24 flex-wrap gap-1 overflow-y-auto">
            {selected.map(value => (
              <Badge
                className="gap-1 font-normal"
                key={value}
                variant="secondary"
              >
                {label(value)}
                <button
                  aria-label={formatMessage(
                    { id: 'filter.remove' },
                    { value: label(value) },
                  )}
                  className="rounded-full"
                  onClick={() => onClickItem(value)}
                  type="button"
                >
                  <IoClose className="size-3" />
                </button>
              </Badge>
            ))}
          </span>
          <PopoverTrigger
            aria-label={title}
            className="flex flex-1 cursor-pointer items-center justify-between gap-2 self-stretch"
            role="combobox"
          >
            {selected.length === 0 && (
              <span className="text-sm text-slate-500">
                {formatMessage({ id: 'filter.select' })}
              </span>
            )}
            <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
          </PopoverTrigger>
          {selected.length > 0 && (
            <button
              aria-label={formatMessage({ id: 'filter.clear' })}
              className="text-dim-gray shrink-0"
              // ponytail: one toggle per value. Callers apply functional updates, so they chain. One onClear if a caller cannot.
              onClick={() => selected.forEach(onClickItem)}
              type="button"
            >
              <IoClose className="size-4" />
            </button>
          )}
        </div>
      </PopoverAnchor>
      <PopoverContent
        align="start"
        className="border-dark-gray w-[var(--radix-popover-trigger-width)] p-0"
      >
        <Command>
          <CommandInput placeholder={formatMessage({ id: 'filter.search' })} />
          <CommandList>
            <CommandEmpty>
              {formatMessage({ id: 'filter.noMatches' })}
            </CommandEmpty>
            <CommandGroup>
              {keys.map(key => (
                <CommandItem
                  key={key}
                  keywords={[label(key)]}
                  onSelect={() => onClickItem(key)}
                  value={key}
                >
                  <Check
                    className={cls(
                      'h-4 w-4',
                      items[key] ? 'opacity-100' : 'opacity-0',
                    )}
                  />
                  <span className="truncate">{label(key)}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

const CheckboxChips = ({
  items,
  onClickItem,
}: Omit<ICheckboxList, 'title'>): JSX.Element => {
  const itemComponents = useMemo(
    () =>
      Object.keys(items).map(key => (
        <CheckboxSectionItem
          key={key}
          value={key}
          onClickItem={onClickItem}
          isSelected={items[key]}
        />
      )),
    [items, onClickItem],
  );

  return <div className="flex flex-wrap gap-2">{itemComponents}</div>;
};

const CheckboxList = ({
  items,
  onClickItem,
  title,
}: ICheckboxList): JSX.Element => {
  if (Object.keys(items).length > CHIP_LIST_LIMIT) {
    return (
      <FilterMultiCombobox
        items={items}
        onClickItem={onClickItem}
        title={title}
      />
    );
  }

  return <CheckboxChips items={items} onClickItem={onClickItem} />;
};

const CheckboxSubsection = ({
  title,
  items,
  onClickItem,
}: ICheckboxSubsection): JSX.Element => {
  return (
    <div>
      <h4 className="text-dim-gray mt-6 mb-2 text-sm font-medium">{title}</h4>
      <CheckboxList items={items} onClickItem={onClickItem} title={title} />
    </div>
  );
};

const CheckboxSection = ({
  items,
  title,
  subtitle,
  onClickItem,
  subsections,
  isGlobal = false,
  className,
  showIcon,
}: ICheckboxSection): JSX.Element => {
  const subsectionComponents = useMemo(
    () =>
      subsections?.map(subsection => (
        <CheckboxSubsection
          key={subsection.title}
          title={subsection.title}
          items={subsection.items}
          onClickItem={subsection.onClickItem}
        />
      )),
    [subsections],
  );

  return (
    <div className={cls(className)}>
      <h3 className="text-dim-gray mb-2 flex items-center gap-[0.4rem] text-base font-semibold">
        {showIcon && <FilterTypeIcon type={isGlobal ? 'global' : 'tab'} />}
        <span>{title}</span>
      </h3>
      {subtitle && <h4 className="text-dim-gray mb-2 text-sm">{subtitle}</h4>}
      {items && (
        <CheckboxList items={items} onClickItem={onClickItem} title={title} />
      )}
      {subsectionComponents}
    </div>
  );
};

export default CheckboxSection;
