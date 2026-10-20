import { useState, type JSX } from 'react';
import { useIntl } from 'react-intl';
import { Check, ChevronsUpDown } from 'lucide-react';
import { IoClose } from 'react-icons/io5';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { useHardwareRegistryFilterOptions } from '@/api/hardware';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import {
  cleanRegistryFilter,
  REGISTRY_FILTER_FIELDS,
  type RegistryFilterKey,
} from './registryFilters';

const HardwareRegistryFilterSelect = ({
  fieldKey,
  label,
  options,
  selected,
  onToggle,
}: {
  fieldKey: string;
  label: string;
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
}): JSX.Element => {
  const intl = useIntl();
  const [open, setOpen] = useState(false);
  const searchPlaceholder = intl.formatMessage({
    id: 'hardwareListing.filterSearch',
  });
  const emptyMessage = intl.formatMessage({
    id: 'hardwareListing.filterEmpty',
  });

  return (
    <Popover onOpenChange={setOpen} open={open}>
      <PopoverTrigger asChild>
        <Button
          aria-expanded={open}
          className={cn(
            'w-[180px] justify-between',
            selected.length === 0 && 'text-slate-500',
          )}
          data-test-id={`registry-filter-${fieldKey}`}
          role="combobox"
          variant="outline"
        >
          <span className="truncate">
            {selected.length > 0 ? `${label} (${selected.length})` : label}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-[220px] p-0">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {options.map(option => (
                <CommandItem
                  key={option}
                  keywords={[option]}
                  onSelect={() => onToggle(option)}
                  value={option}
                >
                  <span className="truncate">{option}</span>
                  <Check
                    className={cn(
                      'ml-auto h-4 w-4 shrink-0',
                      selected.includes(option) ? 'opacity-100' : 'opacity-0',
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

const HardwareRegistryFilters = ({
  startTimestampInSeconds,
  endTimestampInSeconds,
  urlFromMap,
}: {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  urlFromMap: HardwareListingRoutesMap;
}): JSX.Element => {
  const intl = useIntl();
  const navigate = useNavigate({ from: urlFromMap.navigate });
  const { registryFilter } = useSearch({ from: urlFromMap.search });
  const optionsQuery = useHardwareRegistryFilterOptions(
    startTimestampInSeconds,
    endTimestampInSeconds,
    urlFromMap.search,
  );
  const options = optionsQuery.data;

  const setField = (key: RegistryFilterKey, values: string[]): void => {
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        registryFilter: cleanRegistryFilter({
          ...registryFilter,
          [key]: values,
        }),
      }),
      state: s => s,
    });
  };

  const toggle = (key: RegistryFilterKey, value: string): void => {
    const current = registryFilter[key] ?? [];
    setField(
      key,
      current.includes(value)
        ? current.filter(item => item !== value)
        : [...current, value],
    );
  };

  const chips = REGISTRY_FILTER_FIELDS.flatMap(({ key, label }) =>
    (registryFilter[key] ?? []).map(value => ({ key, label, value })),
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-2">
        {REGISTRY_FILTER_FIELDS.map(field => (
          <HardwareRegistryFilterSelect
            key={field.key}
            fieldKey={field.key}
            label={intl.formatMessage({ id: field.label })}
            onToggle={value => toggle(field.key, value)}
            options={options?.[field.optionKey] ?? []}
            selected={registryFilter[field.key] ?? []}
          />
        ))}
      </div>
      {chips.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {chips.map(chip => {
            const label = intl.formatMessage({ id: chip.label });
            return (
              <Badge key={`${chip.key}-${chip.value}`} variant="secondary">
                {label}: {chip.value}
                <button
                  aria-label={intl.formatMessage(
                    { id: 'hardwareListing.filterRemove' },
                    { label, value: chip.value },
                  )}
                  className="ml-1 rounded-full"
                  onClick={() => toggle(chip.key, chip.value)}
                  type="button"
                >
                  <IoClose aria-hidden />
                </button>
              </Badge>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default HardwareRegistryFilters;
