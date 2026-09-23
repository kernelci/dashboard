import { describe, it, expect } from 'vitest';

import type { HardwareItem } from '@/types/hardware';

import { matchesRegistryFilter } from './hardwareListingFilters';

const noStatus = { PASS: 0, FAIL: 0, INCONCLUSIVE: 0 };

const withRegistry: HardwareItem = {
  platform: 'j721e-evm',
  build_status_summary: noStatus,
  boot_status_summary: noStatus,
  test_status_summary: noStatus,
  registry: {
    platform_id: 'j721e-evm',
    vendor: { id: 'ti' },
    processor: { id: 'tda4vm', architecture: 'arm64' },
  },
};

const withoutRegistry: HardwareItem = {
  platform: 'qemu-x86',
  build_status_summary: noStatus,
  boot_status_summary: noStatus,
  test_status_summary: noStatus,
};

describe('matchesRegistryFilter', () => {
  it('requires registry match when a section is active; ANDs sections, ORs values in one', () => {
    const vendorTiOrBeagle = {
      platformVendors: { ti: true, beagleboard: true },
    };

    expect(matchesRegistryFilter(withoutRegistry, vendorTiOrBeagle)).toBe(
      false,
    );
    expect(
      matchesRegistryFilter(withRegistry, {
        ...vendorTiOrBeagle,
        processorArchs: { arm: true },
      }),
    ).toBe(false);
    expect(
      matchesRegistryFilter(withRegistry, {
        ...vendorTiOrBeagle,
        processorArchs: { arm64: true },
      }),
    ).toBe(true);
  });
});
