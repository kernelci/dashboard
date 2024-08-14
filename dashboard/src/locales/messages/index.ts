import { LOCALES } from '../constants';
/*eslint sort-keys: "error"*/

export const messages = {
  [LOCALES.EN_US]: {
    'bootsTab.bootHistory': 'Boot History',
    'bootsTab.bootStatus': 'BootStatus',
    'bootsTab.configs': 'Configs',
    'bootsTab.error': 'Error',
    'bootsTab.errorsSummary': 'Errors Summary',
    'bootsTab.info': 'Info',
    'bootsTab.info.description':
      'ℹ️ There is no boot test data available for this tree',
    'bootsTab.platformsFailingAtBoot': 'Platforms failing at boot',
    'bootsTab.skip': 'Skip',
    'bootsTab.success': 'Success',
    'buildAccordion.buildLogs': 'Build logs',
    'buildAccordion.dtb': 'Dtb',
    'buildAccordion.dtbs': 'dtbs',
    'buildAccordion.kernelConfig': 'Kernel config',
    'buildAccordion.kernelConfigPath': 'config/kernel.config',
    'buildAccordion.kernelImage': 'Kernel image',
    'buildAccordion.logs': 'Logs',
    'buildAccordion.modules': 'Modules',
    'buildAccordion.modulesZip': 'modules.tar.xz',
    'buildAccordion.showMore': 'Show More',
    'buildAccordion.systemMap': 'System map',
    'buildAccordion.systemMapPath': 'kernel/System.map',
    'buildAccordion.testError': 'Test failed',
    'buildAccordion.testSkipped': 'Test skipped',
    'buildAccordion.testStatus': 'Test status',
    'buildAccordion.testSuccess': 'Test success',
    'buildDetails.buildDetails': 'Build Details',
    'buildDetails.buildLogs': 'Build Logs',
    'buildDetails.buildTime': 'Build time',
    'buildDetails.compiler': 'Compiler',
    'buildDetails.gitBranch': 'Git Branch',
    'buildDetails.gitCommit': 'Git Commit',
    'buildDetails.gitDescribe': 'Git Describe',
    'buildDetails.gitUrl': 'Git Url',
    'buildDetails.kernelConfig': 'Kernel Config',
    'buildDetails.kernelImage': 'Kernel Image',
    'buildDetails.noTestResults': 'No test results found.',
    'buildDetails.startTime': 'Start Time',
    'buildDetails.systemMap': 'System Map',
    'buildDetails.testResults': 'Test Results',
    'filter.architectureSubtitle': 'Please select one or more Architectures:',
    'filter.branchSubtitle': 'Please select one or more Branches:',
    'filter.configsSubtitle': 'Please select one or more configs:',
    'filter.filtering': 'Filtering',
    'filter.max': 'Max',
    'filter.min': 'Min',
    'filter.refresh': 'Refresh',
    'filter.statusSubtitle': 'Please select one or more Status:',
    'filter.treeURL': 'Tree URL',
    'global.all': 'All',
    'global.architecture': 'Architecture',
    'global.branch': 'Branch',
    'global.cleanAll': 'Clean all',
    'global.command': 'Command',
    'global.compiler': 'Compiler',
    'global.configs': 'Configs',
    'global.date': 'Date',
    'global.defconfig': 'Defconfig',
    'global.done': 'Done',
    'global.dtb': 'Dtb',
    'global.error': 'Error',
    'global.errors': 'Errors',
    'global.failed': 'Failed',
    'global.filters': 'Filters',
    'global.loading': 'Loading...',
    'global.missed': 'Missed',
    'global.modules': 'Modules',
    'global.name': 'Name',
    'global.none': 'None',
    'global.origins': 'Origins',
    'global.pass': 'Pass',
    'global.seconds': 'sec',
    'global.skiped': 'Skipped',
    'global.somethingWrong': 'Sorry... something went wrong',
    'global.status': 'Status',
    'global.successful': 'Successful',
    'global.timing': 'Timing',
    'global.total': 'Total',
    'global.tree': 'Tree',
    'routes.deviceMonitor': 'Devices',
    'routes.labsMonitor': 'Labs',
    'routes.treeMonitor': 'Revisions',
    'tab.name': 'Name',
    'table.itemsPerPage': 'Items per page:',
    'table.of': 'of',
    'table.showing': 'Showing:',
    'table.tree': 'Tree',
    'treeDetails.arch': 'Arch',
    'treeDetails.boots': 'Boots',
    'treeDetails.buildErrors': 'Build errors',
    'treeDetails.buildStatus': 'Build status',
    'treeDetails.buildTime': 'BuildTime',
    'treeDetails.builds': 'Builds',
    'treeDetails.compiler': 'Compiler',
    'treeDetails.config': 'Config',
    'treeDetails.configs': 'Configs',
    'treeDetails.date': 'Date',
    'treeDetails.executed': 'Executed',
    'treeDetails.failed': 'Failed',
    'treeDetails.null': 'Null',
    'treeDetails.status': 'Status',
    'treeDetails.success': 'Success',
    'treeDetails.summary': 'Summary',
    'treeDetails.tests': 'Tests',
    'treeTable.branch': 'Branch',
    'treeTable.build': 'Build Status (Failed / Total)',
    'treeTable.commit': 'Commit',
    'treeTable.patchset': 'Patchset hash',
    'treeTable.test': 'Test Status (Failed / Total)',
    'treeTable.tree': 'Tree',
  },
};

export type MessagesKey = keyof (typeof messages)['en-us'];
