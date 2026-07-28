import { useState, type JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import FilterDrawer, { DrawerSection } from '@/components/Filter/Drawer';
import { Combobox, type ComboboxOption } from '@/components/Combobox/Combobox';

import type {
  HardwareFiltersResponse,
  HardwareListingFilters,
} from '@/types/hardware';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

/** cmdk keys its items by value, so the "any" choice needs one of its own. */
const ANY_VALUE = '__any__';

const sections = [
  {
    key: 'checkoutOrigin',
    title: 'filter.checkoutOrigin',
    subtitle: 'filter.checkoutOriginSubtitle',
    optionsKey: 'checkout_origins',
  },
  {
    key: 'buildOrigin',
    title: 'filter.buildOrigin',
    subtitle: 'filter.buildOriginSubtitle',
    optionsKey: 'build_origins',
  },
  {
    key: 'buildLab',
    title: 'filter.buildLab',
    subtitle: 'filter.buildLabSubtitle',
    optionsKey: 'build_labs',
  },
  {
    key: 'testOrigin',
    title: 'filter.testOrigin',
    subtitle: 'filter.testOriginSubtitle',
    optionsKey: 'test_origins',
  },
  {
    key: 'testLab',
    title: 'filter.testLab',
    subtitle: 'filter.testLabSubtitle',
    optionsKey: 'test_labs',
  },
] as const;

interface HardwareListingFilterProps {
  data?: HardwareFiltersResponse;
  urlFromMap: HardwareListingRoutesMap;
}

const HardwareListingFilter = ({
  data,
  urlFromMap,
}: HardwareListingFilterProps): JSX.Element => {
  const intl = useIntl();
  const navigate = useNavigate({ from: urlFromMap.navigate });
  const { checkoutOrigin, buildOrigin, testOrigin, buildLab, testLab } =
    useSearch({ from: urlFromMap.search });
  const paramFilter: HardwareListingFilters = {
    checkoutOrigin,
    buildOrigin,
    testOrigin,
    buildLab,
    testLab,
  };

  const [draftFilter, setDraftFilter] =
    useState<HardwareListingFilters>(paramFilter);

  const onClickFilter = (): void => {
    navigate({
      search: previousSearch => ({ ...previousSearch, ...draftFilter }),
      state: s => s,
    });
  };

  const resetDraft = (): void => setDraftFilter(paramFilter);

  const anyLabel = intl.formatMessage({ id: 'filter.anyValue' });

  return (
    <FilterDrawer
      onCancel={resetDraft}
      onFilter={onClickFilter}
      onOpenChange={resetDraft}
      showLegend={false}
    >
      {sections.map(({ key, title, subtitle, optionsKey }, index) => {
        const available = data?.[optionsKey] ?? [];
        const selected = draftFilter[key];
        // A value coming from the URL can be absent from the window's options, and
        // showing it anyway keeps the drawer from looking unset while it still filters
        const values =
          selected && !available.includes(selected)
            ? [selected, ...available]
            : available;

        const options: ComboboxOption[] = [
          { value: ANY_VALUE, label: anyLabel },
          ...values.map(value => ({ value, label: value })),
        ];

        return (
          <DrawerSection key={key} hideSeparator={index === 0}>
            <div className="flex flex-col gap-2">
              <h3 className="text-dim-gray text-xl font-semibold">
                <FormattedMessage id={title} />
              </h3>
              <h4 className="text-dim-gray text-sm">
                <FormattedMessage id={subtitle} />
              </h4>
              <Combobox
                dataTestId={`hardware-filter-${key}`}
                emptyMessage={intl.formatMessage({
                  id: 'filter.noneAvailable',
                })}
                onValueChange={value =>
                  setDraftFilter(previous => ({
                    ...previous,
                    [key]: value === ANY_VALUE ? '' : value,
                  }))
                }
                options={options}
                placeholder={anyLabel}
                searchPlaceholder={intl.formatMessage({
                  id: 'global.search',
                })}
                selectedValue={selected || ANY_VALUE}
              />
            </div>
          </DrawerSection>
        );
      })}
    </FilterDrawer>
  );
};

export default HardwareListingFilter;
