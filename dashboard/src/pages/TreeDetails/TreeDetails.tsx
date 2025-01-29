import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';
import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

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

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import {
  BuildStatus as BuildStatusComponent,
  GroupedTestStatus,
} from '@/components/Status/Status';

import type { TFilter } from '@/types/general';

import MemoizedHardwareUsed from '@/components/Cards/HardwareUsed';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import { truncateUrl } from '@/lib/string';

import CopyButton from '@/components/Button/CopyButton';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';

import { useTreeDetailsLazyLoadQuery } from '@/hooks/useTreeDetailsLazyLoadQuery';

import { LoadingCircle } from '@/components/ui/loading-circle';

import { useQueryInconsistencyInvalidator } from '@/hooks/useQueryInconsistencyInvalidator';

import { statusCountToRequiredStatusCount } from '@/utils/status';

import TreeDetailsFilter from './TreeDetailsFilter';
import type { TreeDetailsTabRightElement } from './Tabs/TreeDetailsTab';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

interface ITreeHeader {
  treeNames?: string;
  gitUrl?: string;
  gitBranch?: string;
  commitName?: string;
  commitHash?: string;
  commitTags?: string[];
}

const defaultUrlLength = 12;

const TreeHeader = ({
  treeNames,
  gitUrl,
  gitBranch,
  commitName,
  commitHash,
  commitTags,
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
          <FormattedMessage id="treeDetails.commitOrTag" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="global.url" />
        </TableHead>
      </DumbTableHeader>
      <TableBody>
        <TableRow>
          {/** TODO: Replace with real data */}
          <TableCell>{treeNames ?? '-'}</TableCell>
          <TableCell>{gitBranch ?? '-'}</TableCell>
          <TableCell>{commitTagTooltip}</TableCell>
          <TableCell>
            <Tooltip>
              <TooltipTrigger>
                {truncateUrl(gitUrl, defaultUrlLength)}
              </TooltipTrigger>
              <TooltipContent>{gitUrl}</TooltipContent>
            </Tooltip>
            {gitUrl && <CopyButton value={gitUrl} />}
          </TableCell>
        </TableRow>
      </TableBody>
    </DumbBaseTable>
  );
};

function TreeDetails(): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId' });
  const searchParams = useSearch({ from: '/tree/$treeId' });
  const { diffFilter, treeInfo } = searchParams;
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const reqFilter = mapFilterToReq(diffFilter);

  const treeDetailsLazyLoaded = useTreeDetailsLazyLoadQuery({
    treeId: treeId ?? '',
    filter: reqFilter,
  });

  const {
    data,
    isLoading,
    error,
    status: summaryQueryStatus,
  } = treeDetailsLazyLoaded.summary;

  const treeRouterStatus = useRouterState({
    select: s => s.location.state.treeStatusCount,
  });

  type TreeRouterStatus = typeof treeRouterStatus;

  const comparedData: TreeRouterStatus = useMemo(() => {
    if (!data) return undefined;

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

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = data?.summary.builds.status ?? {};
    const { status: testStatusSummary } = data?.summary.tests ?? {};

    const { status: bootStatusSummary } = data?.summary.boots ?? {};

    return {
      'global.tests': testStatusSummary ? (
        <GroupedTestStatus
          fail={testStatusSummary.FAIL}
          pass={testStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.boots': bootStatusSummary ? (
        <GroupedTestStatus
          fail={bootStatusSummary.FAIL}
          pass={bootStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.builds': data ? (
        <BuildStatusComponent
          valid={valid}
          invalid={invalid}
          hideInconclusive
        />
      ) : (
        <></>
      ),
    };
  }, [data]);

  return (
    <QuerySwitcher
      status={summaryQueryStatus}
      data={data}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          emptyLabel={'global.error'}
        />
      }
    >
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
          />
        </div>
        <div className="mt-5">
          <MemoizedHardwareUsed
            title={<FormattedMessage id="treeDetails.hardwareUsed" />}
            hardwareUsed={data?.common.hardware}
            diffFilter={diffFilter}
          />
        </div>
        <div className="flex flex-col pb-2">
          <div className="sticky top-[4.5rem] z-10">
            <div className="absolute right-0 top-2 py-4">
              {data ? (
                <TreeDetailsFilter
                  paramFilter={diffFilter}
                  treeUrl={data.common.tree_url}
                  data={data}
                />
              ) : (
                <LoadingCircle className="mr-8 mt-6" />
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
    </QuerySwitcher>
  );
}

export default TreeDetails;
