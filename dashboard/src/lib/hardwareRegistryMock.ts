// MOCK ONLY — frontend preview. Real API later.

export interface HardwareRegistryInfo {
  platformId: string;
  boardType?: string;
  formFactor?: string;
  description?: string;
  url?: string;
  vendor?: { id: string; url?: string };
  siliconVendor?: { id: string; url?: string };
  systemModule?: { id: string; formFactor?: string; url?: string };
  processor?: {
    id: string;
    architecture?: string;
    cores?: number;
    maxClockSpeedMhz?: number;
    url?: string;
    description?: string;
  };
}

const MOCK: HardwareRegistryInfo = {
  platformId: 'am335x-bone-black',
  boardType: 'single_board_computer',
  formFactor: 'board',
  description: 'BeagleBone Black open-source single-board computer',
  url: 'https://beagleboard.org/black',
  vendor: { id: 'beagleboard', url: 'https://beagleboard.org' },
  siliconVendor: { id: 'ti', url: 'https://www.ti.com' },
  systemModule: {
    id: 'osd335x',
    formFactor: 'system-on-module',
    url: 'https://octavosystems.com/octavo_products/osd335x/',
  },
  processor: {
    id: 'am3358',
    architecture: 'arm',
    cores: 1,
    maxClockSpeedMhz: 800,
    url: 'https://www.ti.com/product/AM3358',
    description: 'Arm Cortex-A8, 3D graphics, PRU-ICSS, CAN',
  },
};

export const getMockHardwareRegistryInfo = (
  _platform?: string,
): HardwareRegistryInfo => MOCK;

export const getMockHardwareRegistryListingInfo = (
  platform: string,
  index: number,
): HardwareRegistryInfo | undefined =>
  index === 0 ? { ...MOCK, platformId: platform } : undefined;
