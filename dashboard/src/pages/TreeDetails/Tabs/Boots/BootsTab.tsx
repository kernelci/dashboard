import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import { MemoizedHardwareTested } from '@/components/Cards/HardwareTested';
import {
  type TreeDetailsRouteFrom,
  type PossibleTableFilters,
  treeDetailsFromMap,
  zTableFilterInfoDefault,
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
import { MemoizedOriginsCard } from '@/components/Cards/OriginsCard';
import { sanitizeTreeinfo } from '@/utils/treeDetails';
import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';
import { getStringParam } from '@/utils/utils';

interface BootsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  urlFrom: TreeDetailsRouteFrom;
}

const BootsTab = ({
  treeDetailsLazyLoaded,
  urlFrom,
}: BootsTabProps): JSX.Element => {
  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });
  const params = useParams({
    from: urlFrom,
  });
  const { tableFilter, diffFilter, treeInfo } = useSearch({
    from: urlFrom,
  });

  const sanitizedTreeInfo = useMemo(() => {
    return sanitizeTreeinfo({
      params,
      treeInfo,
      urlFrom,
      summaryUrl: treeDetailsLazyLoaded.summary.data?.common.tree_url,
    });
  }, [
    params,
    treeDetailsLazyLoaded.summary.data?.common.tree_url,
    treeInfo,
    urlFrom,
  ]);

  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

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

  const { treeName, branch, id } = useRouterState({
    select: s => s.location.state,
  });
  const paramsTreeName = getStringParam(params, 'treeName');
  const paramsBranch = getStringParam(params, 'branch');
  const paramsHash = getStringParam(params, 'hash');

  const stateIsSetted = treeName && branch && id;
  const stateParams = useMemo(
    () =>
      !stateIsSetted
        ? { treeName: paramsTreeName, branch: paramsBranch, id: paramsHash }
        : {},
    [stateIsSetted, paramsTreeName, paramsBranch, paramsHash],
  );

  const canGoDirect = paramsTreeName && paramsBranch && paramsHash;

  const getRowLink = useCallback(
    (bootId: string): LinkProps =>
      canGoDirect
        ? {
            to: '/test/$testId',
            params: {
              testId: bootId,
            },
            search: s => ({
              origin: s.origin,
            }),
            state: s => ({ ...s, ...stateParams, from: RedirectFrom.Tree }),
          }
        : {
            to: '/tree/$treeId/test/$testId',
            params: {
              testId: bootId,
              treeId: sanitizedTreeInfo.hash,
            },
            search: s => ({
              origin: s.origin,
            }),
          },
    [stateParams, sanitizedTreeInfo, canGoDirect],
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

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="treeDetails"
        args={{
          cmdName: 'boots',
          'git-url': sanitizedTreeInfo.gitUrl,
          branch: sanitizedTreeInfo.gitBranch,
          commit: sanitizedTreeInfo.hash,
        }}
      />
    ),
    [
      sanitizedTreeInfo.gitBranch,
      sanitizedTreeInfo.gitUrl,
      sanitizedTreeInfo.hash,
    ],
  );

  return (
    <div className="pb-10">
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
              <TreeCommitNavigationGraph
                urlFrom={urlFrom}
                treeName={sanitizedTreeInfo.treeName}
              />
              <MemoizedHardwareTested
                title={<FormattedMessage id="bootsTab.hardwareTested" />}
                environmentCompatible={hardwareData}
                diffFilter={diffFilter}
              />
              <MemoizedOriginsCard
                diffFilter={diffFilter}
                origins={summaryBootsData?.origins ?? {}}
                filterSection="bootOrigin"
              />
            </div>
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={summaryBootsData?.issues ?? []}
              failedWithUnknownIssues={summaryBootsData?.unknown_issues}
              diffFilter={diffFilter}
              issueFilterSection="bootIssue"
              detailsId={sanitizedTreeInfo.hash}
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
            <TreeCommitNavigationGraph
              urlFrom={urlFrom}
              treeName={sanitizedTreeInfo.treeName}
            />
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
                <MemoizedOriginsCard
                  diffFilter={diffFilter}
                  origins={summaryBootsData?.origins ?? {}}
                  filterSection="bootOrigin"
                />
              </div>
              <MemoizedIssuesList
                title={<FormattedMessage id="global.issues" />}
                issues={summaryBootsData?.issues ?? []}
                failedWithUnknownIssues={summaryBootsData?.unknown_issues}
                diffFilter={diffFilter}
                issueFilterSection="bootIssue"
                detailsId={sanitizedTreeInfo.hash}
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
          {kcidevComponent}
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
          <TreeCommitNavigationGraph
            urlFrom={urlFrom}
            treeName={sanitizedTreeInfo.treeName}
          />
        </div>
      )}
    </div>
  );
};

export default BootsTab;
