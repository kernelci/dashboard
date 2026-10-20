import { z } from 'zod';

import type { MessagesKey } from '@/locales/messages';
import type { HardwareRegistryFilterOptions } from '@/types/hardware';

export const REGISTRY_FILTER_FIELDS = [
  {
    key: 'architecture',
    optionKey: 'architecture',
    label: 'hardwareListing.filterArchitecture',
  },
  {
    key: 'processor',
    optionKey: 'processor',
    label: 'hardwareListing.filterProcessor',
  },
  {
    key: 'platformVendor',
    optionKey: 'platform_vendor',
    label: 'hardwareListing.filterPlatformVendor',
  },
  {
    key: 'siliconVendor',
    optionKey: 'silicon_vendor',
    label: 'hardwareListing.filterSiliconVendor',
  },
  {
    key: 'platform',
    optionKey: 'platform',
    label: 'hardwareListing.filterPlatform',
  },
  {
    key: 'systemModule',
    optionKey: 'system_module',
    label: 'hardwareListing.filterSystemModule',
  },
  {
    key: 'formFactor',
    optionKey: 'form_factor',
    label: 'hardwareListing.filterFormFactor',
  },
  {
    key: 'boardType',
    optionKey: 'board_type',
    label: 'hardwareListing.filterBoardType',
  },
] as const satisfies ReadonlyArray<{
  key: string;
  optionKey: keyof HardwareRegistryFilterOptions;
  label: MessagesKey;
}>;

export type RegistryFilterKey = (typeof REGISTRY_FILTER_FIELDS)[number]['key'];

export type TRegistryFilter = Partial<Record<RegistryFilterKey, string[]>>;

export const DEFAULT_REGISTRY_FILTER: TRegistryFilter = {};

const zStringList = z.preprocess(value => {
  if (value === null || value === undefined || value === '') {
    return undefined;
  }
  const values = Array.isArray(value) ? value : [value];
  return values.map(item => String(item)).filter(item => item !== '');
}, z.array(z.string()).optional());

export const zRegistryFilter = z
  .object({
    architecture: zStringList,
    processor: zStringList,
    platformVendor: zStringList,
    siliconVendor: zStringList,
    platform: zStringList,
    systemModule: zStringList,
    formFactor: zStringList,
    boardType: zStringList,
  } satisfies Record<RegistryFilterKey, typeof zStringList>)
  .catch(DEFAULT_REGISTRY_FILTER);

export const cleanRegistryFilter = (
  filter: TRegistryFilter,
): TRegistryFilter => {
  const cleaned: TRegistryFilter = {};
  for (const { key } of REGISTRY_FILTER_FIELDS) {
    const values = filter[key]?.filter(value => value !== '');
    if (values && values.length > 0) {
      cleaned[key] = values;
    }
  }
  return cleaned;
};

export const registryFilterToParams = (
  filter: TRegistryFilter,
): Record<string, string> =>
  Object.fromEntries(
    REGISTRY_FILTER_FIELDS.flatMap(({ key }) => {
      const values = filter[key];
      return values && values.length > 0 ? [[key, values.join(',')]] : [];
    }),
  );

export const hasRegistryFilter = (filter: TRegistryFilter): boolean =>
  REGISTRY_FILTER_FIELDS.some(({ key }) => (filter[key]?.length ?? 0) > 0);
