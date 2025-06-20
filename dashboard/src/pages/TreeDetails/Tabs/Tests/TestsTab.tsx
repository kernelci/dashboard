import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useParams, useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import {
  treeDetailsFromMap,
  type TreeDetailsRouteFrom,
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import MemoizedIssuesList from '@/components/Cards/IssuesList';
import { MemoizedHardwareTested } from '@/components/Cards/HardwareTested';

import { TestsTable } from '@/components/TestsTable/TestsTable';
import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';
import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';
import { RedirectFrom, type TFilterObjectsKeys } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';
import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { generateDiffFilter } from '@/components/Tabs/tabsUtils';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { MemoizedOriginsCard } from '@/components/Cards/OriginsCard';
import { getStringParam } from '@/utils/utils';

interface TestsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  urlFrom: TreeDetailsRouteFrom;
}

const TestsTab = ({
  treeDetailsLazyLoaded,
  urlFrom,
}: TestsTabProps): JSX.Element => {
  const params = useParams({ from: urlFrom });
  const treeId =
    getStringParam(params, 'treeId') || getStringParam(params, 'hash');

  const {
    data: summaryData,
    status: summaryStatus,
    error: summaryError,
    isLoading: summaryIsLoading,
  } = useMemo(
    () => treeDetailsLazyLoaded.summary,
    [treeDetailsLazyLoaded.summary],
  );

  const summaryTestsData = useMemo(
    () => summaryData?.summary.tests,
    [summaryData?.summary.tests],
  );

  const { data: fullData, status: fullStatus } = useMemo(
    () => treeDetailsLazyLoaded.full,
    [treeDetailsLazyLoaded.full],
  );

  const fullTestsData = useMemo(() => fullData?.tests, [fullData?.tests]);

  const { tableFilter, diffFilter } = useSearch({
    from: urlFrom,
  });

  const currentPathFilter = diffFilter.testPath
    ? Object.keys(diffFilter.testPath)[0]
    : undefined;

  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });

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
      });
    },
    [navigate],
  );

  const getRowLink = useCallback(
    (bootId: string): LinkProps => {
      return {
        to: '/tree/$treeId/test/$testId',
        params: {
          testId: bootId,
          treeId: treeId,
        },
        search: s => ({
          origin: s.origin,
        }),
      };
    },
    [treeId],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
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

  const hardwareData = useMemo(() => {
    return {
      ...summaryTestsData?.environment_compatible,
      ...summaryTestsData?.environment_misc,
    };
  }, [
    summaryTestsData?.environment_compatible,
    summaryTestsData?.environment_misc,
  ]);

  const isEmptySummary = useMemo((): boolean => {
    if (!summaryTestsData) {
      return true;
    }
    return Object.values(summaryTestsData.status).every(value => value === 0);
  }, [summaryTestsData]);

  const nonEmptyData = useMemo(() => {
    if (isEmptySummary) {
      return undefined;
    } else {
      return summaryTestsData;
    }
  }, [isEmptySummary, summaryTestsData]);

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
                title={<FormattedMessage id="testsTab.testStatus" />}
                statusCounts={summaryTestsData?.status}
                toggleFilterBySection={toggleFilterBySection}
                filterStatusKey="testStatus"
              />
              <MemoizedConfigList
                title={<FormattedMessage id="global.configs" />}
                configStatusCounts={summaryTestsData?.configs ?? {}}
                diffFilter={diffFilter}
              />
              <MemoizedErrorsSummary
                title={<FormattedMessage id="global.summary" />}
                archCompilerErrors={summaryTestsData?.architectures ?? []}
                diffFilter={diffFilter}
              />
            </div>
            <div>
              <TreeCommitNavigationGraph urlFrom={urlFrom} />
              <MemoizedHardwareTested
                title={<FormattedMessage id="testsTab.hardwareTested" />}
                environmentCompatible={hardwareData}
                diffFilter={diffFilter}
              />
              <MemoizedOriginsCard
                diffFilter={diffFilter}
                origins={summaryTestsData?.origins ?? {}}
                filterSection="testOrigin"
              />
            </div>
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={summaryTestsData?.issues ?? []}
              failedWithUnknownIssues={summaryTestsData?.unknown_issues}
              diffFilter={diffFilter}
              issueFilterSection="testIssue"
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
              title={<FormattedMessage id="testsTab.testStatus" />}
              statusCounts={summaryTestsData?.status}
              toggleFilterBySection={toggleFilterBySection}
              filterStatusKey="testStatus"
            />
            <TreeCommitNavigationGraph urlFrom={urlFrom} />
            <InnerMobileGrid>
              <div>
                <MemoizedConfigList
                  title={<FormattedMessage id="global.configs" />}
                  configStatusCounts={summaryTestsData?.configs ?? {}}
                  diffFilter={diffFilter}
                />
                <MemoizedErrorsSummary
                  title={<FormattedMessage id="global.summary" />}
                  archCompilerErrors={summaryTestsData?.architectures ?? []}
                  diffFilter={diffFilter}
                />
              </div>
              <div>
                <MemoizedHardwareTested
                  title={<FormattedMessage id="testsTab.hardwareTested" />}
                  environmentCompatible={hardwareData}
                  diffFilter={diffFilter}
                />
                <MemoizedOriginsCard
                  diffFilter={diffFilter}
                  origins={summaryTestsData?.origins ?? {}}
                  filterSection="testOrigin"
                />
              </div>
              <MemoizedIssuesList
                title={<FormattedMessage id="global.issues" />}
                issues={summaryTestsData?.issues ?? []}
                failedWithUnknownIssues={summaryTestsData?.unknown_issues}
                diffFilter={diffFilter}
                issueFilterSection="testIssue"
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

          <QuerySwitcher status={fullStatus} data={fullData}>
            <TestsTable
              tableKey="treeDetailsTests"
              testHistory={fullTestsData}
              onClickFilter={onClickFilter}
              filter={tableFilter.testsTable}
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
                  tab: formatMessage({ id: 'global.tests' }).toLowerCase(),
                }}
              />
            </div>
          )}
          <TreeCommitNavigationGraph urlFrom={urlFrom} />
        </div>
      )}
    </div>
  );
};

export default TestsTab;
