import { describe, expect, it } from 'vitest';

import { parseSearch, stringifySearch } from '@/utils/search';

import {
  cleanRegistryFilter,
  registryFilterToParams,
  type TRegistryFilter,
} from './registryFilters';

describe('registryFilterToParams', () => {
  it('omits empty fields and joins selected values', () => {
    const filter: TRegistryFilter = {
      architecture: ['arm64', 'arm'],
      processor: [],
      platform: ['am62-sk'],
    };

    expect(registryFilterToParams(filter)).toEqual({
      architecture: 'arm64,arm',
      platform: 'am62-sk',
    });
  });
});

describe('cleanRegistryFilter', () => {
  it('drops blank and empty lists', () => {
    expect(
      cleanRegistryFilter({
        architecture: ['arm64', ''],
        boardType: [],
      }),
    ).toEqual({ architecture: ['arm64'] });
  });
});

describe('registry filter url', () => {
  it('round-trips every field', () => {
    const registryFilter: TRegistryFilter = {
      architecture: ['arm64', 'arm'],
      processor: ['am625'],
      platformVendor: ['ti'],
      siliconVendor: ['ti'],
      platform: ['am62-sk'],
      systemModule: ['am62-som'],
      formFactor: ['sbc'],
      boardType: ['evaluation_board'],
    };

    expect(parseSearch(stringifySearch({ registryFilter }))).toMatchObject({
      registryFilter,
    });
  });
});
