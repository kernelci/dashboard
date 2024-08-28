import { LOCALES } from '../constants';
/*eslint sort-keys: "error"*/

export const messages = {
  [LOCALES.EN_US]: {
    'bootsTab.bootHistory': 'Boot History',
    'bootsTab.bootStatus': 'Boot Status',
    'bootsTab.configs': 'Configs',
    'bootsTab.error': 'Error',
    'bootsTab.errorsSummary': 'Errors Summary',
    'bootsTab.fail': 'Fail',
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
    'buildAccordion.testDone': 'Test done',
    'buildAccordion.testError': 'Test error',
    'buildAccordion.testFail': 'Test failed',
    'buildAccordion.testMiss': 'Test missed',
    'buildAccordion.testSkipped': 'Test skipped',
    'buildAccordion.testStatus': 'Test status',
    'buildAccordion.testSuccess': 'Test success',
    'buildDetails.buildDetails': 'Build Details',
    'buildDetails.buildLogs': 'Build Logs',
    'buildDetails.buildTime': 'Build time',
    'buildDetails.buildsHistory': 'Builds History',
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
    'filter.bootStatus': 'Boot Status',
    'filter.buildDuration': 'Build duration',
    'filter.buildDurationSubtitle': 'Please select the build duration range:',
    'filter.buildStatus': 'Build Status',
    'filter.compilersSubtitle': 'Please select one or more compilers:',
    'filter.configsSubtitle': 'Please select one or more configs:',
    'filter.filtering': 'Filtering',
    'filter.max': 'Max',
    'filter.min': 'Min',
    'filter.refresh': 'Refresh',
    'filter.statusSubtitle': 'Please select one or more Status:',
    'filter.testStatus': 'Test Status',
    'filter.treeURL': 'Tree URL',
    'global.all': 'All',
    'global.architecture': 'Architecture',
    'global.branch': 'Branch',
    'global.cleanAll': 'Clean all',
    'global.command': 'Command',
    'global.commit': 'Commit',
    'global.compiler': 'Compiler',
    'global.compilers': 'Compilers',
    'global.configs': 'Configs',
    'global.date': 'Date',
    'global.defconfig': 'Defconfig',
    'global.done': 'Done',
    'global.dtb': 'Dtb',
    'global.error': 'Error',
    'global.errors': 'Errors',
    'global.estimate': 'Estimate',
    'global.failed': 'Failed',
    'global.filters': 'Filters',
    'global.info': 'Info',
    'global.loading': 'Loading...',
    'global.missed': 'Missed',
    'global.modules': 'Modules',
    'global.name': 'Name',
    'global.noDataAvailable': 'No data available',
    'global.noResults': 'No results were found',
    'global.none': 'None',
    'global.origin': 'Origin',
    'global.origins': 'Origins',
    'global.pass': 'Pass',
    'global.placeholderSearch': 'Search by tree, branch or tag',
    'global.seconds': 'sec',
    'global.skiped': 'Skipped',
    'global.somethingWrong': 'Sorry... something went wrong',
    'global.status': 'Status',
    'global.successful': 'Successful',
    'global.timing': 'Timing',
    'global.total': 'Total',
    'global.tree': 'Tree',
    'global.unknown': 'Unknown',
    'global.url': 'URL',
    'routes.deviceMonitor': 'Devices',
    'routes.labsMonitor': 'Labs',
    'routes.treeMonitor': 'Trees',
    'tab.name': 'Name',
    'table.itemsPerPage': 'Items per page:',
    'table.of': 'of',
    'table.showing': 'Showing:',
    'table.tree': 'Tree',
    'testDetails.arch': 'Arch',
    'testDetails.compiler': 'Compiler',
    'testDetails.duration': 'Duration',
    'testDetails.errorMessage': 'Error message',
    'testDetails.failedToFetch': 'Failed to fetch test details',
    'testDetails.gitCommitHash': 'Git Commit Hash',
    'testDetails.gitRepositoryBranch': 'Git Repository Branch',
    'testDetails.gitRepositoryUrl': 'Git Repository Url',
    'testDetails.logExcerpt': 'Log Excerpt',
    'testDetails.logUrl': 'Log Url',
    'testDetails.notFound': 'Test not found',
    'testDetails.path': 'Path',
    'testDetails.platform': 'Platform',
    'testDetails.status': 'Status',
    'testStatus.done': 'Done',
    'testStatus.error': 'Error',
    'testStatus.fail': 'Fail',
    'testStatus.miss': 'Miss',
    'testStatus.pass': 'Pass',
    'testStatus.skip': 'Skip',
    'testsTab.errorsSummary': 'Errors Summary',
    'testsTab.fail': 'Fails',
    'testsTab.noTest': 'ℹ️ There is no test data available for this tree',
    'testsTab.platformsErrors': 'Platforms with errors',
    'testsTab.testHistory': 'Test history',
    'testsTab.testStatus': 'Test status',
    'tree.details': 'Trees Details',
    'tree.path': 'Trees',
    'treeDetails.arch': 'Arch',
    'treeDetails.boots': 'Boots',
    'treeDetails.buildErrors': 'Build errors',
    'treeDetails.buildStatus': 'Build status',
    'treeDetails.buildTime': 'Build Time',
    'treeDetails.builds': 'Builds',
    'treeDetails.commitOrTag': 'Commit/Tag',
    'treeDetails.compiler': 'Compiler',
    'treeDetails.config': 'Config',
    'treeDetails.configs': 'Configs',
    'treeDetails.date': 'Date',
    'treeDetails.executed': 'Executed',
    'treeDetails.failed': 'Failed',
    'treeDetails.invalidBuilds': 'Invalid builds',
    'treeDetails.null': 'Null',
    'treeDetails.nullBuilds': 'Null builds',
    'treeDetails.status': 'Status',
    'treeDetails.success': 'Success',
    'treeDetails.summary': 'Summary',
    'treeDetails.tests': 'Tests',
    'treeDetails.unknown': 'Unknown',
    'treeDetails.validBuilds': 'Valid builds',
    'treeTable.bootStatus': 'Boot Status',
    'treeTable.branch': 'Branch',
    'treeTable.build': 'Build Status',
    'treeTable.commitTag': 'Commit/Tag',
    'treeTable.patchset': 'Patchset hash',
    'treeTable.test': 'Test Status',
    'treeTable.tree': 'Tree',
  },
};

export type MessagesKey = keyof (typeof messages)['en-us'];
