export const COMMON_SELECTORS = {
  tableRow: 'tr',
  tableHeader: 'th',

  originDropdown: '[data-test-id="origin-dropdown"]',
  originOption: (origin: string) => `[data-test-id="origin-option-${origin}"]`,
} as const;
