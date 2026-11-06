import { useCallback, useMemo, useState, type JSX } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterDrawer from '@/components/Filter/Drawer';
import { MemoizedCheckboxSection } from '@/components/Tabs/Filters';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import type { HardwareFiltersResponse, HardwareItem } from '@/types/hardware';
import {
  HARDWARE_LISTING_FILTER_SECTIONS,
  hardwareListingFilterSections,
} from '@/utils/constants/hardwareListingFilters';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import {
  cleanRegistryFilter,
  createRegistryFilter,
  isRegistryFilterKey,
  registryFilterSections,
  type TRegistryFilter,
} from './hardwareListingFilters';

const createFilter = (
  data: HardwareFiltersResponse | undefined,
  paramFilter: TFilter,
): TFilter => {
  const filters: TFilter = {};

  for (const { sectionKey, optionsKey } of HARDWARE_LISTING_FILTER_SECTIONS) {
    const section: Record<string, boolean> = {};
    for (const value of data?.[optionsKey] ?? []) {
      section[value] = false;
    }

    const current = paramFilter[sectionKey];
    if (current && typeof current === 'object') {
      for (const [value, checked] of Object.entries(current)) {
        if (!(value in section)) {
          section[value] = checked;
        }
      }
    }

    filters[sectionKey] = section;
  }

  return filters;
};

interface HardwareListingFilterProps {
  paramFilter: TFilter;
  data?: HardwareFiltersResponse;
  navigateFrom: HardwareListingRoutesMap['navigate'];
}

export const HardwareListingFilter = ({
  paramFilter,
  data,
  navigateFrom,
}: HardwareListingFilterProps): JSX.Element => {
  const navigate = useNavigate({ from: navigateFrom });
  const filter = useMemo(
    () => createFilter(data, paramFilter),
    [data, paramFilter],
  );
  const [diffFilter, setDiffFilter] = useState<TFilter>(paramFilter);

  const onFilter = useCallback(() => {
    const cleanedFilter = cleanFalseFilters(diffFilter);
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        diffFilter: cleanedFilter,
      }),
      state: s => s,
    });
  }, [diffFilter, navigate]);

  const resetDraft = useCallback(
    () => setDiffFilter(paramFilter),
    [paramFilter],
  );

  return (
    <FilterDrawer
      onCancel={resetDraft}
      onFilter={onFilter}
      onOpenChange={resetDraft}
      showLegend={false}
    >
      <MemoizedCheckboxSection
        diffFilter={diffFilter}
        filter={filter}
        isTFilterObjectKeys={isTFilterObjectKeys}
        sections={hardwareListingFilterSections}
        setDiffFilter={setDiffFilter}
        showAllIcons={false}
      />
    </FilterDrawer>
  );
};

export const RegistryListingFilter = ({
  paramFilter,
  items,
  urlFromMap,
}: {
  paramFilter: TRegistryFilter;
  items: HardwareItem[];
  urlFromMap: HardwareListingRoutesMap;
}): JSX.Element => {
  const navigate = useNavigate({ from: urlFromMap.navigate });
  const filter = useMemo(() => createRegistryFilter(items), [items]);
  const [diffFilter, setDiffFilter] = useState<TRegistryFilter>(paramFilter);

  const onClickFilterHandle = useCallback(() => {
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        registryFilter: cleanRegistryFilter(diffFilter),
      }),
      state: s => s,
    });
  }, [diffFilter, navigate]);

  const resetToParamFilter = useCallback(
    () => setDiffFilter(paramFilter),
    [paramFilter],
  );

  return (
    <FilterDrawer
      onFilter={onClickFilterHandle}
      onOpenChange={resetToParamFilter}
      onCancel={resetToParamFilter}
      showLegend={false}
    >
      <MemoizedCheckboxSection
        sections={registryFilterSections}
        setDiffFilter={setDiffFilter}
        diffFilter={diffFilter}
        filter={filter}
        isTFilterObjectKeys={isRegistryFilterKey}
        showAllIcons={false}
      />
    </FilterDrawer>
  );
};
