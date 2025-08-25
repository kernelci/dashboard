import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import type {
  HardwareDetailsSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import { MemoizedResponsiveDetailsCards } from '@/components/Tabs/TabGrid';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';
import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';
import HardwareCommitNavigationGraph from '@/pages/hardwareDetails/Tabs/HardwareCommitNavigationGraph';
import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';

import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import HardwareDetailsTestTable from './HardwareDetailsTestsTable';

interface ITestsTab {
  hardwareId: string;
  trees: HardwareDetailsSummary['common']['trees'];
  testsSummary: HardwareDetailsSummary['summary']['tests'];
  fullDataResult?: UseQueryResult<THardwareDetails>;
}

const TestsTab = ({
  hardwareId,
  trees,
  testsSummary,
  fullDataResult,
}: ITestsTab): JSX.Element => {
  const { tableFilter, diffFilter, origin } = useSearch({
    from: '/_main/hardware/$hardwareId',
  });

  const currentPathFilter = diffFilter.testPath
    ? Object.keys(diffFilter.testPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const updatePathFilter = useCallback(
    (pathFilter: string) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          diffFilter: {
            ...previousSearch.diffFilter,
            testPath: pathFilter === '' ? undefined : { [pathFilter]: true },
          },
        }),
        state: s => s,
      });
    },
    [navigate],
  );

  const onClickFilter = useCallback(
    (newFilter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: newFilter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const toggleFilterBySection = useCallback(
    (filterSectionKey: string, filterSection: TFilterObjectsKeys): void => {
      navigate({
        search: previousParams => {
          const { diffFilter: currentDiffFilter } = previousParams;
          const newFilter = generateDiffFilter(
            filterSectionKey,
            filterSection,
            currentDiffFilter,
          );

          return {
            ...previousParams,
            diffFilter: newFilter,
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="hardwareDetails"
        args={{
          cmdName: 'hardware tests',
          name: hardwareId,
          origin: origin,
          json: true,
        }}
      />
    ),
    [hardwareId, origin],
  );

  const { topCards, bodyCards, footerCards } = useMemo(() => {
    return {
      topCards: [
        <MemoizedStatusCard
          key="statusGraph"
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={testsSummary.status}
          toggleFilterBySection={toggleFilterBySection}
          filterStatusKey="testStatus"
        />,
        <HardwareCommitNavigationGraph
          key="commitGraph"
          trees={trees}
          hardwareId={hardwareId}
        />,
      ],
      bodyCards: [
        <MemoizedErrorsSummary
          key="errorsSummary"
          title={<FormattedMessage id="global.summary" />}
          archCompilerErrors={testsSummary.architectures}
          diffFilter={diffFilter}
        />,
        <MemoizedConfigList
          key="configs"
          title={<FormattedMessage id="bootsTab.configs" />}
          configStatusCounts={testsSummary.configs}
          diffFilter={diffFilter}
        />,
      ],
      footerCards: [
        <MemoizedIssuesList
          key="issues"
          title={<FormattedMessage id="global.issues" />}
          issues={testsSummary.issues}
          failedWithUnknownIssues={testsSummary.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="testIssue"
          detailsId={hardwareId}
          pageFrom={RedirectFrom.Hardware}
        />,
      ],
    };
  }, [diffFilter, hardwareId, testsSummary, toggleFilterBySection, trees]);

  return (
    <div className="flex flex-col gap-8 pt-4 pb-10">
      <MemoizedResponsiveDetailsCards
        topCards={topCards}
        bodyCards={bodyCards}
        footerCards={footerCards}
      />
      <HardwareDetailsTabsQuerySwitcher
        fullDataResult={fullDataResult}
        tabData={fullDataResult?.data?.tests}
      >
        <HardwareDetailsTestTable
          tableKey="hardwareDetailsTests"
          testHistory={fullDataResult?.data?.tests}
          filter={tableFilter.testsTable}
          hardwareId={hardwareId}
          onClickFilter={onClickFilter}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
        />
      </HardwareDetailsTabsQuerySwitcher>
      {kcidevComponent}
    </div>
  );
};
export default TestsTab;
