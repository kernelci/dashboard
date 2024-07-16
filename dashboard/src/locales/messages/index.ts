import { LOCALES } from '../constants';

export const messages = {
  [LOCALES.EN_US]: {
    global: {
      filters: 'Filters',
      cleanAll: 'Clean all',
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
    treeDetails: {
      arch: 'Arch',
      boots: 'Boots',
      builds: 'Builds',
      configs: 'Configs',
      compiler: 'Compiler',
      summary: 'Summary',
      tests: 'Tests',
    },
    treeTable: {
      branch: 'Branch',
      build: 'Build Status (Failed / Total)',
      commit: 'Tag - Commit',
      test: 'Test Status (Failed / Total)',
      tree: 'Tree',
    },
    filter: {
      min: 'Min',
      max: 'Max',
      filtering: 'Filtering',
      treeURL: 'Tree URL',
      refresh: 'Refresh',
    },
  },
};
