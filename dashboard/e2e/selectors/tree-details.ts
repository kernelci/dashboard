export const TREE_DETAILS_SELECTORS = {
  breadcrumbTreesLink: '[data-test-id="breadcrumb-trees-link"]',

  treeHeaderTable: 'table',

  tabs: {
    builds: 'button:has-text("Builds")',
    boots: 'button:has-text("Boots")',
    tests: 'button:has-text("Tests")',
  },

  filters: {
    button: 'button:has-text("Filters")',
    drawer: 'aside',
    drawerContent: '[role="dialog"]',
    filterButton: '[data-test-id="filter-button"]',
    cancelButton: '[data-test-id="filter-cancel-button"]',
    clearAllFilters: 'text="Clear all"',
  },

  buildHistoryGraph: 'img',

  statusCard: {
    title: '.flex-col:has(div:has-text("Build status"))',
    titleFirst: '.flex-col:has(div:has-text("Build status"))',
    statusButton: (status: string) => `[data-test-id="${status}"]`,
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
    detailsButton: '[data-test-id="details-button"]',
  },

  bootsTable: {
    statusFilters: {
      all: 'button:has-text("All:")',
      success: 'button:has-text("Success:")',
      failed: 'button:has-text("Failed:")',
      inconclusive: 'button:has-text("Inconclusive:")',
    },
    detailsButton: '[data-test-id="details-button"]',
  },

  testsTable: {
    statusFilters: {
      all: 'button:has-text("All:")',
      success: 'button:has-text("Success:")',
      failed: 'button:has-text("Failed:")',
      inconclusive: 'button:has-text("Inconclusive:")',
    },
    testItem: 'tr',
    expandedRows: 'tr:has(td[colspan])',
    detailsButton: '[data-test-id="details-button"]',
  },

  configTable: {
    link: (config: string) => `a:has-text("${config}")`,
  },

  commitGraph: {
    container: '[data-test-id="commit-navigation-graph"]',
    svg: '[data-test-id="commit-navigation-graph"] svg',
    marks: '[data-test-id="commit-navigation-graph"] [class*="MuiMarkElement"]',
  },
} as const;
