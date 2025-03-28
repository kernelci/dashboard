import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';
import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';

import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';
import { RedirectFrom } from '@/types/general';
import type { PropertyStatusCounts, TFilterObjectsKeys } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';
import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { generateDiffFilter } from '@/components/Tabs/tabsUtils';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

interface BootsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
}

const BootsTab = ({ treeDetailsLazyLoaded }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/_main/tree/$treeId',
  });

  const { tableFilter, diffFilter } = useSearch({
    from: '/_main/tree/$treeId',
  });

  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/tree/$treeId' });

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

  const {
    data: summaryData,
    status: summaryStatus,
    error: summaryError,
    isLoading: summaryIsLoading,
  } = useMemo(
    () => treeDetailsLazyLoaded.summary,
    [treeDetailsLazyLoaded.summary],
  );

  const summaryBootsData = useMemo(
    () => summaryData?.summary.boots,
    [summaryData?.summary.boots],
  );

  const { data: fullData, status: fullStatus } = useMemo(
    () => treeDetailsLazyLoaded.full,
    [treeDetailsLazyLoaded.full],
  );

  const bootsData = useMemo(() => fullData?.boots, [fullData?.boots]);

  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: bootId,
        treeId: treeId,
      },
      search: s => ({
        origin: s.origin,
      }),
    }),
    [treeId],
  );

  const hardwareData = useMemo((): PropertyStatusCounts => {
    return {
      ...summaryBootsData?.environment_compatible,
      ...summaryBootsData?.environment_misc,
    };
  }, [summaryBootsData]);

  const isEmptySummary = useMemo((): boolean => {
    if (!summaryBootsData) {
      return true;
    }
    return Object.values(summaryBootsData.status).every(value => value === 0);
  }, [summaryBootsData]);

  const nonEmptyData = useMemo(() => {
    if (isEmptySummary) {
      return undefined;
    } else {
      return summaryBootsData;
    }
  }, [isEmptySummary, summaryBootsData]);

  const { formatMessage } = useIntl();

  return (
    <div>
      <QuerySwitcher
        data={nonEmptyData}
        status={summaryStatus}
        skeletonClassname="max-h-[100px]"
        customError={
          <MemoizedSectionError
            isLoading={summaryIsLoading}
            errorMessage={summaryError?.message}
            forceErrorMessageUse
            variant="warning"
          />
        }
      >
        <div className="flex flex-col gap-8 pt-4">
          <DesktopGrid>
            <div>
              <MemoizedStatusCard
                title={<FormattedMessage id="bootsTab.bootStatus" />}
                statusCounts={summaryBootsData?.status}
                toggleFilterBySection={toggleFilterBySection}
                filterStatusKey="bootStatus"
              />
              <MemoizedConfigList
                title={<FormattedMessage id="bootsTab.configs" />}
                configStatusCounts={summaryBootsData?.configs ?? {}}
                diffFilter={diffFilter}
              />
              <MemoizedErrorsSummary
                title={<FormattedMessage id="global.summary" />}
                archCompilerErrors={summaryBootsData?.architectures ?? []}
                diffFilter={diffFilter}
              />
            </div>
            <div>
              <TreeCommitNavigationGraph />
              <MemoizedHardwareTested
                title={<FormattedMessage id="bootsTab.hardwareTested" />}
                environmentCompatible={hardwareData}
                diffFilter={diffFilter}
              />
            </div>
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={summaryBootsData?.issues ?? []}
              failedWithUnknownIssues={summaryBootsData?.unknown_issues}
              diffFilter={diffFilter}
              issueFilterSection="bootIssue"
              detailsId={treeId}
              pageFrom={RedirectFrom.Tree}
              issueExtraDetails={
                treeDetailsLazyLoaded.issuesExtras.data?.issues
              }
              extraDetailsLoading={treeDetailsLazyLoaded.issuesExtras.isLoading}
            />
          </DesktopGrid>
          <MobileGrid>
            <MemoizedStatusCard
              title={<FormattedMessage id="bootsTab.bootStatus" />}
              statusCounts={summaryBootsData?.status}
              toggleFilterBySection={toggleFilterBySection}
              filterStatusKey="bootStatus"
            />
            <TreeCommitNavigationGraph />
            <InnerMobileGrid>
              <div>
                <MemoizedConfigList
                  title={<FormattedMessage id="bootsTab.configs" />}
                  configStatusCounts={summaryBootsData?.configs ?? {}}
                  diffFilter={diffFilter}
                />
                <MemoizedErrorsSummary
                  title={<FormattedMessage id="global.summary" />}
                  archCompilerErrors={summaryBootsData?.architectures ?? []}
                  diffFilter={diffFilter}
                />
              </div>
              <div>
                <MemoizedHardwareTested
                  title={<FormattedMessage id="bootsTab.hardwareTested" />}
                  environmentCompatible={hardwareData}
                  diffFilter={diffFilter}
                />
              </div>
              <MemoizedIssuesList
                title={<FormattedMessage id="global.issues" />}
                issues={summaryBootsData?.issues ?? []}
                failedWithUnknownIssues={summaryBootsData?.unknown_issues}
                diffFilter={diffFilter}
                issueFilterSection="bootIssue"
                detailsId={treeId}
                pageFrom={RedirectFrom.Tree}
                issueExtraDetails={
                  treeDetailsLazyLoaded.issuesExtras.data?.issues
                }
                extraDetailsLoading={
                  treeDetailsLazyLoaded.issuesExtras.isLoading
                }
              />
            </InnerMobileGrid>
          </MobileGrid>
          <QuerySwitcher data={bootsData} status={fullStatus}>
            <BootsTable
              tableKey="treeDetailsBoots"
              filter={tableFilter.bootsTable}
              onClickFilter={onClickFilter}
              testHistory={bootsData ?? []}
              getRowLink={getRowLink}
              updatePathFilter={updatePathFilter}
              currentPathFilter={currentPathFilter}
            />
          </QuerySwitcher>
        </div>
      </QuerySwitcher>
      {isEmptySummary && (
        <div className="mx-48 max-2xl:mx-0">
          {summaryError !== null && (
            <div className="px-4 pb-2">
              <FormattedMessage
                id="tab.findOnPreviousCheckoutsTooltip"
                values={{
                  tab: formatMessage({ id: 'global.boots' }).toLowerCase(),
                }}
              />
            </div>
          )}
          <TreeCommitNavigationGraph />
        </div>
      )}
    </div>
  );
};

export default BootsTab;
