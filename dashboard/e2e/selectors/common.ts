export const COMMON_SELECTORS = {
  tableRow: 'tr',
  tableHeader: 'th',

  originDropdown: '[data-test-id="origin-dropdown"]',
  originOption: (origin: string) => `[data-test-id="origin-option-${origin}"]`,

  STATUS_FILTER_TEXT: {
    ALL: 'All:',
    SUCCESS: 'Success:',
    FAILED: 'Failed:',
    INCONCLUSIVE: 'Inconclusive:',
  },
  statusFilterSelector: (status: string) => `button:has-text("${status}")`,

  STATUS_LABEL_TEXT: {
    PASS: 'PASS',
    FAIL: 'FAIL',
    ERROR: 'ERROR',
    MISS: 'MISS',
    SKIP: 'SKIP',
    DONE: 'DONE',
    NULL: 'NULL',
  },
  SECTION_TEXT: {
    BUILD_STATUS: 'Build Status',
    BOOT_STATUS: 'Boot Status',
  },
  statusLabelSelector: (section: string, status: string) =>
    `text="${section}" >> .. >> label:has-text("${status}")`,
} as const;
