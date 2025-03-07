import React from 'react';

import { FEEDBACK_EMAIL_TO } from '@/utils/constants/general';

import { LOCALES } from '../constants';
/*eslint sort-keys: "error"*/

export const formattedBreakLineValue = { br: React.createElement('br') };

export const messages = {
  [LOCALES.EN_US]: {
    'boots.statusTooltip':
      'Success - boots with PASS status{br}' +
      'Failed - boots with FAIL status{br}' +
      'Inconclusive - boot concluded with inconclusive results such as infrastructure errors.{br}{br}' +
      'Inconclusive groups boots with ERROR, MISS, SKIP, DONE, and unknown statuses defined by KCIDB.',
    'bootsTab.bootStatus': 'Boot Status',
    'bootsTab.configs': 'Configs',
    'bootsTab.error': 'Error',
    'bootsTab.hardwareTested': 'Hardware tested',
    'bootsTab.info': 'Info',
    'bootsTab.info.description':
      'ℹ️ There is no boot test data available for this tree',
    'bootsTab.success': 'Success',
    'build.dummyInfo': 'Dummy builds are hidden from this table',
    'build.statusTooltip':
      'Success - builds completed successfully{br}' +
      'Failed - builds failed{br}' +
      "Inconclusive - builds with unknown status, including ongoing builds that didn't finish yet.",
    'buildDetails.buildDetails': 'Build Details',
    'buildDetails.buildId': 'Build Id',
    'buildDetails.buildLogs': 'Build Logs',
    'buildDetails.gitDescribe': 'Git Describe',
    'buildDetails.kernelConfig': 'Kernel Config',
    'buildDetails.noTestResults': 'No test results found.',
    'buildDetails.startTime': 'Start Time',
    'buildDetails.testResults': 'Test Results',
    'buildTab.buildStatus': 'Build status',
    'codeBlock.highlights': 'Highlights:',
    'codeBlock.highlightsTooltip': 'Counting estimated based on text output',
    'commonDetails.artifacts': 'Artifacts',
    'commonDetails.environmentMiscData': 'Environment Misc Data',
    'commonDetails.gitCommitHash': 'Git Commit Hash',
    'commonDetails.gitCommitName': 'Git Commit Name',
    'commonDetails.gitCommitTag': 'Git Commit Tag',
    'commonDetails.gitRepositoryBranch': 'Git Repository Branch',
    'commonDetails.gitRepositoryUrl': 'Git Repository Url',
    'commonDetails.miscData': 'Misc Data',
    'filter.architectureSubtitle': 'Please select one or more Architectures:',
    'filter.bootDuration': 'Boot duration',
    'filter.bootIssue': 'Boot issue',
    'filter.bootPlatform': 'Boot Platforms',
    'filter.bootStatus': 'Boot Status',
    'filter.buildDuration': 'Build duration',
    'filter.buildIssue': 'Build Issue',
    'filter.buildStatus': 'Build Status',
    'filter.compatiblesSubtitle': 'Please select one or more compatibles:',
    'filter.compilersSubtitle': 'Please select one or more compilers:',
    'filter.configsSubtitle': 'Please select one or more configs:',
    'filter.durationSubtitle': 'Please select the duration range:',
    'filter.filtering': 'Filtering',
    'filter.globalFilter': 'Global filters',
    'filter.globalFilterAllTabs': 'Global filters affects all the tabs',
    'filter.hardware': 'Hardware',
    'filter.hardwareSubtitle': 'Please select one or more hardwares:',
    'filter.invalid': 'Please provide a time limit, in days, greater than 0',
    'filter.issueSubtitle': 'Please select one or more issues:',
    'filter.max': 'Max',
    'filter.min': 'Min',
    'filter.onlySpecificTab': 'Only affects a specific tab',
    'filter.perTabFilter': 'Per tab filters',
    'filter.platformSubtitle': 'Please select one or more platforms:',
    'filter.statusSubtitle': 'Please select one or more Status:',
    'filter.tableFilter': 'Status filters:',
    'filter.testDuration': 'Test duration',
    'filter.testIssue': 'Test issue',
    'filter.testPlatform': 'Test Platforms',
    'filter.testStatus': 'Test Status',
    'filter.treeSubtitle': 'Please select one or more Trees:',
    'filter.treeURL': 'Tree URL',
    'global.allCount': 'All: {count}',
    'global.arch': 'Arch',
    'global.architecture': 'Architecture',
    'global.arrowDown': 'Down Arrow',
    'global.arrowLeft': 'Left Arrow',
    'global.arrowRight': 'Right Arrow',
    'global.arrowUp': 'Up Arrow',
    'global.boots': 'Boots',
    'global.buildErrors': 'Build errors',
    'global.buildTime': 'Build Time',
    'global.builds': 'Builds',
    'global.cancel': 'Cancel',
    'global.cleanAll': 'Clean all',
    'global.close': 'Close',
    'global.command': 'Command',
    'global.compatibles': 'Compatibles',
    'global.compiler': 'Compiler',
    'global.compilers': 'Compilers',
    'global.config': 'Config',
    'global.configs': 'Configs',
    'global.date': 'Date',
    'global.days': 'Days',
    'global.details': 'Details',
    'global.documentation': 'Documentation',
    'global.duration': 'Duration',
    'global.email': 'Email',
    'global.error': 'Error',
    'global.errors': 'Errors',
    'global.executed': 'Executed',
    'global.failed': 'Failed',
    'global.failedCount': 'Failed: {count}',
    'global.fails': 'Fails',
    'global.filters': 'Filters',
    'global.fullLogs': 'Full logs',
    'global.github': 'GitHub',
    'global.hardware': 'Hardware',
    'global.hardwares': 'Hardwares',
    'global.inconclusive': 'Inconclusive',
    'global.inconclusiveCount': 'Inconclusive: {count}',
    'global.info': 'Info',
    'global.issues': 'Issues',
    'global.last': 'Last',
    'global.legend': 'Legend',
    'global.loading': 'Loading...',
    'global.logExcerpt': 'Log Excerpt',
    'global.logs': 'Logs',
    'global.modules': 'Modules',
    'global.name': 'Name',
    'global.new': 'New',
    'global.next': 'Next',
    'global.noDataAvailable': 'No data available',
    'global.noResults': 'No results were found',
    'global.origin': 'Origin',
    'global.others': 'Others',
    'global.path': 'Path',
    'global.platform': 'Platform',
    'global.prev': 'Prev',
    'global.projectUnderDevelopment':
      'This is an ongoing project.{br}' +
      `Please report bugs and suggestions to ${FEEDBACK_EMAIL_TO}.`,
    'global.search': 'Search',
    'global.seconds': 'sec',
    'global.showMoreDetails': 'Show more details',
    'global.somethingWrong': 'Sorry... something went wrong',
    'global.startTime': 'Start Time',
    'global.status': 'Status',
    'global.success': 'Success',
    'global.successCount': 'Success: {count}',
    'global.summary': 'Summary',
    'global.tests': 'Tests',
    'global.timeAgo': '{time} ago',
    'global.tree': 'Tree',
    'global.treeBranch': 'Tree / Branch',
    'global.trees': 'Trees',
    'global.underDevelopment': 'Under Development',
    'global.unknown': 'Unknown',
    'global.url': 'URL',
    'global.viewJson': 'View Json',
    'global.viewLog': 'View Log Excerpt',
    'global.warning': 'Warning',
    'globalTable.bootStatus': 'Boot Status',
    'globalTable.branch': 'Branch',
    'globalTable.build': 'Build Status',
    'globalTable.commitTag': 'Commit/Tag',
    'globalTable.test': 'Test Status',
    'globalTable.tree': 'Tree',
    'hardware.details': 'Hardware Details',
    'hardware.multiplePlatforms': 'Multiple Platforms',
    'hardware.path': 'Hardware',
    'hardware.searchPlaceholder':
      'Search by hardware name or platform with a regex',
    'hardwareDetails.platforms': 'Platforms',
    'hardwareDetails.timeFrame':
      'Results from {startDate} and {startTime} to {endDate} {endTime}',
    'hardwareListing.description': 'List of hardware from kernel tests',
    'hardwareListing.title': 'Hardware Listing ― KCI Dashboard',
    'issue.alsoPresentTooltip': 'Issue also present in {tree}',
    'issue.firstSeen': 'First seen',
    'issue.newIssue': 'New issue: This is the first time this issue was seen',
    'issue.noIssueFound': 'No issue found.',
    'issue.path': 'Issues',
    'issue.searchPlaceholder': 'Search by issue comment with a regex',
    'issue.tooltip':
      'Issues groups several builds or tests by matching result status and logs.{br}They may also be linked to an external issue tracker or mailing list discussion.',
    'issue.uncategorized': 'Uncategorized',
    'issueDetails.buildValid': 'Build Valid',
    'issueDetails.comment': 'Comment',
    'issueDetails.culpritCode': 'Code',
    'issueDetails.culpritHarness': 'Harness',
    'issueDetails.culpritTitle': 'Culprit',
    'issueDetails.culpritTool': 'Tool',
    'issueDetails.firstIncidentData': 'First Incident Data',
    'issueDetails.id': 'Issue Id',
    'issueDetails.issueDetails': 'Issue Details',
    'issueDetails.logspecData': 'Logspec Data',
    'issueDetails.notFound': 'Issue not found',
    'issueDetails.reportSubject': 'Report Subject',
    'issueDetails.reportUrl': 'Report URL',
    'issueDetails.version': 'Version',
    'issueListing.culpritInfo':
      'Layers of the execution stack responsible for the issue.  If all are false, the issue is considered invalid.',
    'issueListing.description': 'List of issues from builds and tests',
    'issueListing.title': 'Issue Listing ― KCI Dashboard',
    'issueListing.treeBranchTooltip':
      'The tree name and git repository branch of the first incident\nClick a cell to see details of that checkout',
    'jsonSheet.title': 'JSON Viewer',
    'logSheet.downloadLog': 'You can download the full log here: {link}',
    'logSheet.fileName': 'File Name',
    'logSheet.fileSize': 'File Size',
    'logSheet.logQueryCustomError':
      'This log url is not supported in the log viewer yet, but you can still download the log in the link above',
    'logSheet.noLogFound': 'No logs available',
    'logSheet.title': 'Logs Viewer',
    'logspec.info':
      "This is the same logspec data that's in the misc data section",
    'routes.buildDetails': 'Build',
    'routes.hardwareMonitor': 'Hardware',
    'routes.issueDetails': 'Issue',
    'routes.issueMonitor': 'Issues',
    'routes.sendFeedback': 'Send us Feedback',
    'routes.sendFeedbackMsg':
      'Thank you for your feedback!\nWe greatly appreciate your input. You are welcome to send us the feedback via email or by creating an issue on our GitHub repository.',
    'routes.testDetails': 'Test',
    'routes.treeMonitor': 'Trees',
    'routes.unknown': 'Unknown',
    'tab.name': 'Name',
    'table.itemsPerPage': 'Items per page:',
    'table.of': 'of',
    'table.showing': 'Showing:',
    'tag.failCount': '{count} Fail',
    'tag.inconclusiveCount': '{count} Inconclusive',
    'tag.noBuildsOrTestsData': 'No builds or tests data.',
    'tag.passCount': '{count} Pass',
    'test.details': 'Test Details',
    'test.statusTooltip':
      'Success - tests with PASS status{br}' +
      'Failed - tests with FAIL status{br}' +
      'Inconclusive - test concluded with inconclusive results such as infrastructure errors.{br}{br}' +
      'Inconclusive groups tests with ERROR, MISS, SKIP, DONE, and unknown statuses defined by KCIDB.',
    'testDetails.buildInfo': 'Build Info',
    'testDetails.notFound': 'Test not found',
    'testDetails.regressionTypeTooltip':
      'The regression type of the test.\n' +
      'Pass - test passed in all previous tests\n' +
      'Fail - test failed in all previous tests\n' +
      'Fixed - test was failing but passed in the last iterations\n' +
      'Regression - test was passing but failed in the last iterations\n' +
      'Unstable - test has inconclusive results or is not consistent',
    'testDetails.statusHistory': 'Status History',
    'testDetails.statusHistoryTooltip':
      'The {amount} previous tests before the current test.\nClick on an icon to see details of that specific test.',
    'testDetails.testId': 'Test Id',
    'testStatus.done': 'Done',
    'testStatus.error': 'Error',
    'testStatus.fail': 'Fail',
    'testStatus.miss': 'Miss',
    'testStatus.pass': 'Pass',
    'testStatus.skip': 'Skip',
    'testsTab.hardwareTested': 'Hardware tested',
    'testsTab.noTest': 'ℹ️ There is no test data available for this tree',
    'testsTab.testStatus': 'Test status',
    'title.buildDetails': 'Build: {buildName}',
    'title.default': 'KernelCI Dashboard',
    'title.hardwareDetails': 'Hardware: {hardwareName}',
    'title.issueDetails': 'Issue: {issueName}',
    'title.testDetails': 'Test: {testName}',
    'title.treeDetails': 'Tree: {treeName}',
    'tree.details': 'Trees Details',
    'tree.path': 'Trees',
    'tree.searchPlaceholder': 'Search by tree, branch or tag with a regex',
    'treeDetails.bootsHistory': 'Boots History',
    'treeDetails.branch': 'Branch',
    'treeDetails.buildsHistory': 'Builds History',
    'treeDetails.commitOrTag': 'Commit/Tag',
    'treeDetails.failedBoots': 'Failed boots',
    'treeDetails.hardwareUsed': 'Hardware Used',
    'treeDetails.inconclusiveBoots': 'Inconclusive Boots',
    'treeDetails.inconclusiveBuilds': 'Inconclusive Builds',
    'treeDetails.inconclusiveTests': 'Inconclusive Tests',
    'treeDetails.invalidBuilds': 'Failed builds',
    'treeDetails.successBoots': 'Success boots',
    'treeDetails.testsFailed': 'Failed tests',
    'treeDetails.testsHistory': 'Tests History',
    'treeDetails.testsInconclusive': 'Inconclusive tests',
    'treeDetails.testsSuccess': 'Success tests',
    'treeDetails.validBuilds': 'Success builds',
    'treeListing.description': 'List of trees for kernel builds and tests',
    'treeListing.title': 'Tree Listing ― KCI Dashboard',
  },
};

export type MessagesKey = keyof (typeof messages)['en-us'];
