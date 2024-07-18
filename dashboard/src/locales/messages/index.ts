import { LOCALES } from '../constants';

export const messages = {
  [LOCALES.EN_US]: {
    global: {
      all: 'All',
      cleanAll: 'Clean all',
      errors: 'Errors',
      filters: 'Filters',
      seconds: 'sec',
      successful: 'Successful',
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
      buildErrors: 'Build errors',
      buildStatus: 'Build status',
      buildTime: 'BuildTime',
      config: 'Config',
      configs: 'Configs',
      compiler: 'Compiler',
      date: 'Date',
      executed: 'Executed',
      summary: 'Summary',
      status: 'Status',
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
