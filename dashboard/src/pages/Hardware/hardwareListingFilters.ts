import { z } from 'zod';

import type { ISectionItem } from '@/components/Filter/CheckboxSection';
import type { MessagesKey } from '@/locales/messages';
import type { HardwareItem, HardwareRegistryInfo } from '@/types/hardware';

type RegistryFilterField = {
  key: string;
  title: MessagesKey;
  subtitle: MessagesKey;
  value: (registry?: HardwareRegistryInfo | null) => string | null | undefined;
};

const REGISTRY_FILTER_FIELDS = [
  {
    key: 'platformVendors',
    title: 'filter.platformVendors',
    subtitle: 'filter.platformVendorsSubtitle',
    value: (r): string | null | undefined => r?.vendor?.id,
  },
  {
    key: 'platformBoardTypes',
    title: 'filter.platformBoardTypes',
    subtitle: 'filter.platformBoardTypesSubtitle',
    value: (r): string | null | undefined => r?.board_type,
  },
  {
    key: 'processorIds',
    title: 'filter.processorIds',
    subtitle: 'filter.processorIdsSubtitle',
    value: (r): string | null | undefined => r?.processor?.id,
  },
  {
    key: 'processorVendors',
    title: 'filter.processorVendors',
    subtitle: 'filter.processorVendorsSubtitle',
    value: (r): string | null | undefined => r?.silicon_vendor?.id,
  },
  {
    key: 'processorArchs',
    title: 'filter.processorArchs',
    subtitle: 'filter.processorArchsSubtitle',
    value: (r): string | null | undefined => r?.processor?.architecture,
  },
] as const satisfies ReadonlyArray<RegistryFilterField>;

type RegistryFilterKey = (typeof REGISTRY_FILTER_FIELDS)[number]['key'];

export type TRegistryFilter = Partial<
  Record<RegistryFilterKey, Record<string, boolean>>
>;

const registryFilterKeys = REGISTRY_FILTER_FIELDS.map(field => field.key) as [
  RegistryFilterKey,
  ...RegistryFilterKey[],
];

export const DEFAULT_REGISTRY_FILTER: TRegistryFilter = {};

export const zRegistryFilter = z
  .record(z.enum(registryFilterKeys), z.record(z.boolean()))
  .default(DEFAULT_REGISTRY_FILTER)
  .catch(DEFAULT_REGISTRY_FILTER);

export const isRegistryFilterKey = (key: string): boolean =>
  registryFilterKeys.includes(key as RegistryFilterKey);

export const registryFilterSections: ISectionItem[] =
  REGISTRY_FILTER_FIELDS.map(({ key, title, subtitle }) => ({
    title,
    subtitle,
    sectionKey: key,
  }));

const selectedIn = (section?: Record<string, boolean>): string[] =>
  Object.keys(section ?? {}).filter(value => section?.[value]);

export const createRegistryFilter = (
  items: HardwareItem[],
): TRegistryFilter => {
  const filter: TRegistryFilter = {};

  for (const item of items) {
    for (const { key, value } of REGISTRY_FILTER_FIELDS) {
      const option = value(item.registry);
      if (option) {
        (filter[key] ??= {})[option] = false;
      }
    }
  }

  return filter;
};

export const matchesRegistryFilter = (
  item: HardwareItem,
  filter: TRegistryFilter,
): boolean =>
  REGISTRY_FILTER_FIELDS.every(({ key, value }) => {
    const selected = selectedIn(filter[key]);
    return (
      selected.length === 0 || selected.includes(value(item.registry) ?? '')
    );
  });

export const cleanRegistryFilter = (filter: TRegistryFilter): TRegistryFilter =>
  Object.fromEntries(
    REGISTRY_FILTER_FIELDS.map(({ key }) => [key, selectedIn(filter[key])])
      .filter(([, selected]) => selected.length > 0)
      .map(([key, selected]) => [
        key,
        Object.fromEntries((selected as string[]).map(value => [value, true])),
      ]),
  );
