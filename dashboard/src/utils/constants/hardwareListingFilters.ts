import type { ISectionItem } from '@/components/Filter/CheckboxSection';
import type { TFilterObjectsKeys } from '@/types/general';
import type { HardwareFiltersResponse } from '@/types/hardware';

export const HARDWARE_LISTING_FILTER_SECTIONS = [
  {
    sectionKey: 'testLabs',
    optionsKey: 'test_labs',
    paramKey: 'testLab',
    title: 'hardwareFilter.testLab',
    subtitle: 'hardwareFilter.testLabSubtitle',
  },
  {
    sectionKey: 'checkoutOrigins',
    optionsKey: 'checkout_origins',
    paramKey: 'checkoutOrigin',
    title: 'hardwareFilter.checkoutOrigin',
    subtitle: 'hardwareFilter.checkoutOriginSubtitle',
  },
  {
    sectionKey: 'buildOrigin',
    optionsKey: 'build_origins',
    paramKey: 'buildOrigin',
    title: 'hardwareFilter.buildOrigin',
    subtitle: 'hardwareFilter.buildOriginSubtitle',
  },
  {
    sectionKey: 'buildLabs',
    optionsKey: 'build_labs',
    paramKey: 'buildLab',
    title: 'hardwareFilter.buildLab',
    subtitle: 'hardwareFilter.buildLabSubtitle',
  },
  {
    sectionKey: 'testOrigin',
    optionsKey: 'test_origins',
    paramKey: 'testOrigin',
    title: 'hardwareFilter.testOrigin',
    subtitle: 'hardwareFilter.testOriginSubtitle',
  },
] as const satisfies ReadonlyArray<
  ISectionItem & {
    sectionKey: TFilterObjectsKeys;
    optionsKey: keyof HardwareFiltersResponse;
    paramKey: string;
  }
>;

export const hardwareListingFilterSections: ISectionItem[] =
  HARDWARE_LISTING_FILTER_SECTIONS.map(({ title, subtitle, sectionKey }) => ({
    title,
    subtitle,
    sectionKey,
  }));
