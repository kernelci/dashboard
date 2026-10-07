import { useCallback, useMemo, useState, type JSX } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterDrawer from '@/components/Filter/Drawer';

import { MemoizedCheckboxSection } from '@/components/Tabs/Filters';

import type { HardwareItem } from '@/types/hardware';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import {
  cleanRegistryFilter,
  createRegistryFilter,
  isRegistryFilterKey,
  registryFilterSections,
  type TRegistryFilter,
} from './hardwareListingFilters';

const HardwareListingFilter = ({
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

export default HardwareListingFilter;
