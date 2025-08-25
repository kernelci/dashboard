import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';

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
import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';
import { HardwareDetailsTabsQuerySwitcher } from '@/pages/hardwareDetails/Tabs/HardwareDetailsTabsQuerySwitcher';
import { generateDiffFilter } from '@/components/Tabs/tabsUtils';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { HardwareDetailsBootsTable } from './HardwareDetailsBootsTable';

interface IBootsTab {
  hardwareId: string;
  trees: HardwareDetailsSummary['common']['trees'];
  bootsSummary: HardwareDetailsSummary['summary']['boots'];
  fullDataResult?: UseQueryResult<THardwareDetails>;
}

const BootsTab = ({
  hardwareId,
  trees,
  bootsSummary,
  fullDataResult,
}: IBootsTab): JSX.Element => {
  const { tableFilter, diffFilter, origin } = useSearch({
    from: '/_main/hardware/$hardwareId',
  });

  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/hardware/$hardwareId/test/$testId',
      params: {
        testId: bootId,
        hardwareId: hardwareId,
      },
      search: s => ({
        origin: s.origin,
      }),
    }),
    [hardwareId],
  );

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const updatePathFilter = useCallback(
    (pathFilter: string) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          diffFilter: {
            ...previousSearch.diffFilter,
            bootPath: pathFilter === '' ? undefined : { [pathFilter]: true },
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
              bootsTable: newFilter,
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
          cmdName: 'hardware boots',
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
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={bootsSummary.status}
          toggleFilterBySection={toggleFilterBySection}
          filterStatusKey="bootStatus"
        />,
        <HardwareCommitNavigationGraph
          key="commitGraph"
          trees={trees}
          hardwareId={hardwareId}
        />,
      ],
      bodyCards: [
        <MemoizedErrorsSummary
          key="errorSummary"
          title={<FormattedMessage id="global.summary" />}
          archCompilerErrors={bootsSummary.architectures}
          diffFilter={diffFilter}
        />,
        <MemoizedConfigList
          key="configs"
          title={<FormattedMessage id="bootsTab.configs" />}
          configStatusCounts={bootsSummary.configs}
          diffFilter={diffFilter}
        />,
      ],
      footerCards: [
        <MemoizedIssuesList
          key="issues"
          title={<FormattedMessage id="global.issues" />}
          issues={bootsSummary.issues}
          failedWithUnknownIssues={bootsSummary.unknown_issues}
          diffFilter={diffFilter}
          issueFilterSection="bootIssue"
          detailsId={hardwareId}
          pageFrom={RedirectFrom.Hardware}
        />,
      ],
    };
  }, [bootsSummary, diffFilter, hardwareId, toggleFilterBySection, trees]);

  return (
    <div className="flex flex-col gap-8 pt-4 pb-10">
      <MemoizedResponsiveDetailsCards
        topCards={topCards}
        bodyCards={bodyCards}
        footerCards={footerCards}
      />
      <HardwareDetailsTabsQuerySwitcher
        fullDataResult={fullDataResult}
        tabData={fullDataResult?.data?.boots}
      >
        <HardwareDetailsBootsTable
          tableKey="hardwareDetailsBoots"
          getRowLink={getRowLink}
          filter={tableFilter.bootsTable}
          testHistory={fullDataResult?.data?.boots}
          onClickFilter={onClickFilter}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
        />
      </HardwareDetailsTabsQuerySwitcher>
      {kcidevComponent}
    </div>
  );
};
export default BootsTab;
