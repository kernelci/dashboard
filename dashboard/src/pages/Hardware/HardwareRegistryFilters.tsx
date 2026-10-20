import { useCallback, useMemo, useState, type JSX } from 'react';
import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { useHardwareRegistryFilterOptions } from '@/api/hardware';
import FilterCheckboxSection from '@/components/Filter/CheckboxSection';
import FilterDrawer, { DrawerSection } from '@/components/Filter/Drawer';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import {
  cleanRegistryFilter,
  REGISTRY_FILTER_FIELDS,
  type RegistryFilterKey,
  type TRegistryFilter,
} from './registryFilters';

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
  const [draft, setDraft] = useState<TRegistryFilter>(registryFilter);

  const handleOpenChange = useCallback(() => {
    setDraft(registryFilter);
  }, [registryFilter]);

  const onFilter = useCallback(() => {
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        registryFilter: cleanRegistryFilter(draft),
      }),
      state: s => s,
    });
  }, [draft, navigate]);

  const sections = useMemo(
    () =>
      REGISTRY_FILTER_FIELDS.flatMap(field => {
        const choices = optionsQuery.data?.[field.optionKey] ?? [];
        if (choices.length === 0) {
          return [];
        }
        const selected = new Set(draft[field.key] ?? []);
        return [
          {
            key: field.key,
            title: intl.formatMessage({ id: field.label }),
            items: Object.fromEntries(
              choices.map(choice => [choice, selected.has(choice)]),
            ),
          },
        ];
      }),
    [draft, intl, optionsQuery.data],
  );

  const toggle = useCallback((key: RegistryFilterKey, value: string): void => {
    setDraft(current => {
      const values = current[key] ?? [];
      const nextValues = values.includes(value)
        ? values.filter(item => item !== value)
        : [...values, value];
      return cleanRegistryFilter({ ...current, [key]: nextValues });
    });
  }, []);

  return (
    <FilterDrawer
      onCancel={handleOpenChange}
      onFilter={onFilter}
      onOpenChange={handleOpenChange}
      showLegend={false}
    >
      {sections.map((section, index) => (
        <DrawerSection hideSeparator={index === 0} key={section.key}>
          <FilterCheckboxSection
            items={section.items}
            onClickItem={value => toggle(section.key, value)}
            showIcon={false}
            title={section.title}
          />
        </DrawerSection>
      ))}
    </FilterDrawer>
  );
};

export default HardwareRegistryFilters;
