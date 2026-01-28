export const TREE_LISTING_SELECTORS = {
  table: 'table',
  treeColumnHeader: 'th button:has-text("Tree")',
  branchColumnHeader: 'th button:has-text("Branch")',

  intervalInput: 'input[type="number"][min="1"]',

  // This requires nth() selector which can't be stored as string
  itemsPerPageDropdown: '[role="listbox"]',
  itemsPerPageOption: (value: string) => `[role="option"]:has-text("${value}")`,

  searchInput: 'input[type="text"]',

  nextPageButton: '[role="button"]:has-text(">")',
  previousPageButton: '[role="button"]:has-text("<")',

  treeNameCell: (treeName: string) => `td a:has-text("${treeName}")`,
  firstTreeCell: 'td a',

  breadcrumbTreesLink: '[data-test-id="breadcrumb-link"]:has-text("Trees")',
} as const;

export const COMMON_SELECTORS = {
  tableRow: 'tr',
  tableHeader: 'th',

  originDropdown: '[data-test-id="origin-dropdown"]',
  originOption: (origin: string) => `[data-test-id="origin-option-${origin}"]`,
} as const;

export const TREE_DETAILS_SELECTORS = {
  breadcrumbTreesLink: '[data-test-id="breadcrumb-link"]',

  treeHeaderTable: 'table',

  tabs: {
    builds: 'button:has-text("Builds")',
    boots: 'button:has-text("Boots")',
    tests: 'button:has-text("Tests")',
  },

  filters: {
    button: 'button:has-text("Filters")',
    drawer: 'aside',
    filterButton: 'button:has-text("Filter")',
    cancelButton: 'button:has-text("Cancel")',
    clearAllFilters: 'text="Clear all"',
  },

  buildHistoryGraph: 'img',

  statusCard: {
    title: '.flex-col:has(div:has-text("Build status"))',
    titleFirst: '.flex-col:has(div:has-text("Build status"))',
    statusButton: (status: string) => `button:has-text("${status}")`,
  },

  summaryCards: {
    arch: 'text="Summary"',
  },

  issuesCard: {
    title: 'text="Issues"',
    button: 'button[aria-label="Issues"]',
  },

  buildTable: {
    table: 'table',
    statusFilters: {
      all: 'button:has-text("All:")',
      success: 'button:has-text("Success:")',
      failed: 'button:has-text("Failed:")',
      inconclusive: 'button:has-text("Inconclusive:")',
    },
    searchInput: 'input[placeholder*="Search"]',
    detailsButton: 'a[href^="/build/"]',
  },

  bootsTable: {
    statusFilters: {
      all: 'button:has-text("All:")',
      success: 'button:has-text("Success:")',
      failed: 'button:has-text("Failed:")',
      inconclusive: 'button:has-text("Inconclusive:")',
    },
    detailsButton: 'a[href^="/test/"]',
  },

  testsTable: {
    statusFilters: {
      all: 'button:has-text("All:")',
      success: 'button:has-text("Success:")',
      failed: 'button:has-text("Failed:")',
      inconclusive: 'button:has-text("Inconclusive:")',
    },
    testItem: 'tr',
    detailsButton: 'a[href^="/test/"]',
  },

  configTable: {
    link: (config: string) => `a:has-text("${config}")`,
  },
} as const;
