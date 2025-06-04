import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';
import type { JSX } from 'react';
import { useCallback, useEffect, useMemo } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import { useSearchStore } from '@/hooks/store/useSearchStore';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import {
  DumbBaseTable,
  DumbTableHeader,
  TableHead,
} from '@/components/Table/BaseTable';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { GroupedTestStatus } from '@/components/Status/Status';

import type { TFilter } from '@/types/general';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import { truncateUrl } from '@/lib/string';

import CopyButton from '@/components/Button/CopyButton';

import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';

import { useTreeDetailsLazyLoadQuery } from '@/hooks/useTreeDetailsLazyLoadQuery';

import { LoadingCircle } from '@/components/ui/loading-circle';

import { useQueryInconsistencyInvalidator } from '@/hooks/useQueryInconsistencyInvalidator';

import type { GroupedStatus } from '@/utils/status';
import { groupStatus, statusCountToRequiredStatusCount } from '@/utils/status';

import PageWithTitle from '@/components/PageWithTitle';

import { MemoizedTreeHardwareDetailsOGTags } from '@/components/OpenGraphTags/TreeHardwareDetailsOGTags';

import type { TabRightElementRecord } from '@/components/Tabs/Tabs';
import { isEmptyObject } from '@/utils/utils';

import TreeDetailsFilter from './TreeDetailsFilter';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

interface ITreeHeader {
  treeNames?: string;
  gitUrl?: string;
  gitBranch?: string;
  commitName?: string;
  commitHash?: string;
  commitTags?: string[];
  origin?: string;
}

const defaultUrlLength = 12;

const getTreeName = (
  treeId: string,
  treeName?: string,
  gitBranch?: string,
): string => {
  if (!treeName && !gitBranch) {
    return treeId;
  }
  if (!treeName) {
    return gitBranch ?? '';
  }
  if (!gitBranch) {
    return treeName;
  }
  return `${treeName}/${gitBranch}`;
};

const TreeHeader = ({
  treeNames,
  gitUrl,
  gitBranch,
  commitName,
  commitHash,
  commitTags,
  origin,
}: ITreeHeader): JSX.Element => {
  const commitTagTooltip = useMemo(
    () => (
      <CommitTagTooltip
        commitName={commitName}
        commitHash={commitHash}
        commitTags={commitTags}
        copyButton={true}
      />
    ),
    [commitName, commitHash, commitTags],
  );

  return (
    <DumbBaseTable>
      <DumbTableHeader>
        <TableHead>
          <FormattedMessage id="global.tree" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="treeDetails.branch" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="global.origin" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="treeDetails.commitOrTag" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="global.url" />
        </TableHead>
      </DumbTableHeader>
      <TableBody>
        <TableRow>
          <TableCell>{treeNames ?? '-'}</TableCell>
          <TableCell>{gitBranch ?? '-'}</TableCell>
          <TableCell>{origin ?? '-'}</TableCell>
          <TableCell>{commitTagTooltip}</TableCell>
          <TableCell>
            <div>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span>{truncateUrl(gitUrl, defaultUrlLength)}</span>
                </TooltipTrigger>
                <TooltipContent>{gitUrl}</TooltipContent>
              </Tooltip>
              {gitUrl && <CopyButton value={gitUrl} />}
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </DumbBaseTable>
  );
};

function TreeDetails(): JSX.Element {
  const { formatMessage } = useIntl();

  const { treeId } = useParams({ from: '/_main/tree/$treeId' });
  const searchParams = useSearch({ from: '/_main/tree/$treeId' });
  const { diffFilter, treeInfo } = searchParams;
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const updatePreviousSearch = useSearchStore(s => s.updatePreviousSearch);

  useEffect(
    () => updatePreviousSearch(searchParams),
    [searchParams, updatePreviousSearch],
  );

  const reqFilter = mapFilterToReq(diffFilter);

  const treeDetailsLazyLoaded = useTreeDetailsLazyLoadQuery({
    treeId: treeId ?? '',
    filter: reqFilter,
  });

  const { data, isLoading } = treeDetailsLazyLoaded.summary;

  const treeRouterStatus = useRouterState({
    select: s => s.location.state.treeStatusCount,
  });

  type TreeRouterStatus = typeof treeRouterStatus;

  const comparedData: TreeRouterStatus = useMemo(() => {
    if (!data) {
      return undefined;
    }

    const { builds, tests, boots } = data.summary;

    return {
      builds: builds.status,
      tests: statusCountToRequiredStatusCount(tests.status),
      boots: statusCountToRequiredStatusCount(boots.status),
    } satisfies TreeRouterStatus;
  }, [data]);

  useQueryInconsistencyInvalidator<TreeRouterStatus>({
    referenceData: treeRouterStatus,
    comparedData: comparedData,
    navigate: navigate,
    enabled: isEmptyObject(reqFilter),
  });
  const onFilterChange = useCallback(
    (newFilter: TFilter) => {
      navigate({
        search: previousSearch => {
          return {
            ...previousSearch,
            diffFilter: newFilter,
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const cleanAll = useCallback(() => {
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: {},
        };
      },
      state: s => s,
    });
  }, [navigate]);

  const filterListElement = useMemo(
    () => (
      <DetailsFilterList
        filter={diffFilter}
        cleanFilters={cleanAll}
        navigate={onFilterChange}
        isLoading={treeDetailsLazyLoaded.summary.isPlaceholderData}
      />
    ),
    [
      cleanAll,
      diffFilter,
      onFilterChange,
      treeDetailsLazyLoaded.summary.isPlaceholderData,
    ],
  );

  const [buildStatusCount, bootStatusCount, testStatusCount]: [
    GroupedStatus,
    GroupedStatus,
    GroupedStatus,
  ] = useMemo(() => {
    const { status: buildStatusSummary } = data?.summary.builds ?? {};
    const { status: testStatusSummary } = data?.summary.tests ?? {};
    const { status: bootStatusSummary } = data?.summary.boots ?? {};

    const buildCount = groupStatus({
      passCount: buildStatusSummary?.PASS,
      failCount: buildStatusSummary?.FAIL,
      doneCount: buildStatusSummary?.DONE,
      errorCount: buildStatusSummary?.ERROR,
      missCount: buildStatusSummary?.MISS,
      skipCount: buildStatusSummary?.SKIP,
      nullCount: buildStatusSummary?.NULL,
    });

    const bootCount = groupStatus({
      passCount: bootStatusSummary?.PASS,
      failCount: bootStatusSummary?.FAIL,
      doneCount: bootStatusSummary?.DONE,
      errorCount: bootStatusSummary?.ERROR,
      missCount: bootStatusSummary?.MISS,
      skipCount: bootStatusSummary?.SKIP,
      nullCount: bootStatusSummary?.NULL,
    });

    const testCount = groupStatus({
      passCount: testStatusSummary?.PASS,
      failCount: testStatusSummary?.FAIL,
      doneCount: testStatusSummary?.DONE,
      errorCount: testStatusSummary?.ERROR,
      missCount: testStatusSummary?.MISS,
      skipCount: testStatusSummary?.SKIP,
      nullCount: testStatusSummary?.NULL,
    });

    return [buildCount, bootCount, testCount];
  }, [data?.summary.boots, data?.summary.builds, data?.summary.tests]);

  const tabsCounts: TabRightElementRecord = useMemo(() => {
    return {
      testTab: (
        <GroupedTestStatus
          preCalculatedGroupedStatus={testStatusCount}
          hideInconclusive
        />
      ),
      bootTab: (
        <GroupedTestStatus
          preCalculatedGroupedStatus={bootStatusCount}
          hideInconclusive
        />
      ),
      buildTab: (
        <GroupedTestStatus
          preCalculatedGroupedStatus={buildStatusCount}
          hideInconclusive
        />
      ),
    };
  }, [bootStatusCount, buildStatusCount, testStatusCount]);

  const treeDetailsTitle = formatMessage(
    { id: 'title.treeDetails' },
    {
      treeName: getTreeName(treeId, treeInfo.treeName, treeInfo.gitBranch),
    },
  );

  return (
    <PageWithTitle title={treeDetailsTitle}>
      <MemoizedTreeHardwareDetailsOGTags
        title={treeDetailsTitle}
        buildCount={buildStatusCount}
        bootCount={bootStatusCount}
        testCount={testStatusCount}
      />
      <div className="flex flex-col pt-8">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink
                to="/tree"
                search={previousParams => {
                  return {
                    intervalInDays: previousParams.intervalInDays,
                    origin: previousParams.origin,
                  };
                }}
                state={s => s}
              >
                <FormattedMessage id="tree.path" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>
                <FormattedMessage id="tree.details" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <div className="mt-5">
          <TreeHeader
            gitBranch={treeInfo?.gitBranch}
            treeNames={treeInfo?.treeName}
            gitUrl={treeInfo?.gitUrl}
            commitHash={treeId}
            commitName={treeInfo?.commitName}
            commitTags={data?.common.git_commit_tags}
            origin={searchParams.origin}
          />
        </div>
        <div className="flex flex-col pb-2">
          <div className="sticky top-[4.5rem] z-10">
            <div className="absolute top-2 right-0 py-4">
              {data ? (
                <TreeDetailsFilter
                  paramFilter={diffFilter}
                  treeUrl={data.common.tree_url}
                  data={data}
                />
              ) : (
                isLoading && <LoadingCircle className="mt-6 mr-8" />
              )}
            </div>
          </div>
          <TreeDetailsTab
            treeDetailsLazyLoaded={treeDetailsLazyLoaded}
            filterListElement={filterListElement}
            countElements={tabsCounts}
          />
        </div>
      </div>
    </PageWithTitle>
  );
}

export default TreeDetails;
