import { LOCALES } from '../constants';

export const messages = {
  [LOCALES.EN_US]: {
    global: {
      filters: 'Filters',
    },
    routes: {
      deviceMonitor: 'Devices',
      labsMonitor: 'Labs',
      treeMonitor: 'Trees',
    },
    table: {
      itemsPerPage: 'Items per page:',
      of: 'of',
      showing: 'Showing:',
      tree: 'Tree',
    },
    treeTable: {
      branch: 'Branch',
      build: 'Build Status (Failed / Total)',
      commit: 'Tag - Commit',
      test: 'Test Status (Failed / Total)',
      tree: 'Tree',
    },
  },
};
