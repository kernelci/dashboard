export const TREE_LISTING_SELECTORS = {
  table: 'table',
  treeColumnHeader: 'th button:has-text("Tree")',
  branchColumnHeader: 'th button:has-text("Branch")',

  intervalInput: 'input[type="number"][min="1"]',

  itemsPerPageDropdown: '[role="listbox"]',
  itemsPerPageOption: (value: string) => `[role="option"]:has-text("${value}")`,

  searchInput: 'input[type="text"]',

  nextPageButton: '[role="button"]:has-text(">")',
  previousPageButton: '[role="button"]:has-text("<")',

  treeNameCell: (treeName: string) => `td a:has-text("${treeName}")`,
  firstTreeCell: 'td a',

  breadcrumbTreesLink: '[data-test-id="breadcrumb-link"]:has-text("Trees")',
} as const;
