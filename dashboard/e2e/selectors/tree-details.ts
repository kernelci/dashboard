import { COMMON_SELECTORS } from './common';

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
    buildStatusSection: `text="${COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS}"`,
    bootStatusSection: `text="${COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS}"`,
    buildStatus: {
      pass: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.PASS,
      ),
      fail: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.FAIL,
      ),
      error: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.ERROR,
      ),
      miss: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.MISS,
      ),
      skip: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.SKIP,
      ),
      done: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.DONE,
      ),
      null: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BUILD_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.NULL,
      ),
    },
    bootStatus: {
      pass: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.PASS,
      ),
      fail: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.FAIL,
      ),
      error: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.ERROR,
      ),
      miss: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.MISS,
      ),
      skip: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.SKIP,
      ),
      done: COMMON_SELECTORS.statusLabelSelector(
        COMMON_SELECTORS.SECTION_TEXT.BOOT_STATUS,
        COMMON_SELECTORS.STATUS_LABEL_TEXT.DONE,
      ),
    },
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
      all: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.ALL,
      ),
      success: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.SUCCESS,
      ),
      failed: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.FAILED,
      ),
      inconclusive: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.INCONCLUSIVE,
      ),
    },
    searchInput: 'input[placeholder*="Search"]',
    detailsButton: '[data-test-id="details-button"]',
  },

  bootsTable: {
    statusFilters: {
      all: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.ALL,
      ),
      success: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.SUCCESS,
      ),
      failed: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.FAILED,
      ),
      inconclusive: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.INCONCLUSIVE,
      ),
    },
    detailsButton: '[data-test-id="details-button"]',
  },

  testsTable: {
    statusFilters: {
      all: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.ALL,
      ),
      success: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.SUCCESS,
      ),
      failed: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.FAILED,
      ),
      inconclusive: COMMON_SELECTORS.statusFilterSelector(
        COMMON_SELECTORS.STATUS_FILTER_TEXT.INCONCLUSIVE,
      ),
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
