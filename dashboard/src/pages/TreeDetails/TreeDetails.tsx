import { useParams, useSearch } from '@tanstack/react-router';
import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useBuildsTab, useTestsTab } from '@/api/TreeDetails';
import type { IListingItem } from '@/components/ListingItem/ListingItem';
import type { ISummaryItem } from '@/components/Summary/Summary';
import type { AccordionItemBuilds, BuildsTab } from '@/types/tree/TreeDetails';
import { Skeleton } from '@/components/Skeleton';
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

import { sanitizeTableValue } from '@/components/Table/tableUtils';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import {
  BuildStatus as BuildStatusComponent,
  GroupedTestStatus,
} from '@/components/Status/Status';

import {
  sanitizeArchs,
  sanitizeBuilds,
  sanitizeBuildsSummary,
  sanitizeConfigs,
} from '@/utils/utils';

import type { BuildStatus } from '@/types/general';

import MemoizedHardwareUsed from '@/components/Cards/HardwareUsed';

import TreeDetailsFilter, { mapFilterToReq } from './TreeDetailsFilter';
import type { TreeDetailsTabRightElement } from './Tabs/TreeDetailsTab';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

import TreeDetailsFilterList from './TreeDetailsFilterList';

export interface ITreeDetails {
  architectures: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: BuildStatus;
  builds: AccordionItemBuilds[];
  issues: BuildsTab['issues'];
}

interface ITreeHeader {
  commit?: string;
  treeNames?: string;
  tag?: string;
  gitUrl?: string;
  gitBranch?: string;
}

const TreeHeader = ({
  commit,
  treeNames,
  tag,
  gitUrl,
  gitBranch,
}: ITreeHeader): JSX.Element => {
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
          <TableCell>
            <Tooltip>
              <TooltipTrigger>{sanitizeTableValue(tag, false)}</TooltipTrigger>
              <TooltipContent>{commit}</TooltipContent>
            </Tooltip>
          </TableCell>
          <TableCell>
            <Tooltip>
              <TooltipTrigger>{sanitizeTableValue(gitUrl)} </TooltipTrigger>
              <TooltipContent>{gitUrl}</TooltipContent>
            </Tooltip>
          </TableCell>
        </TableRow>
      </TableBody>
    </DumbBaseTable>
  );
};

function TreeDetails(): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const searchParams = useSearch({ from: '/tree/$treeId/' });
  const { diffFilter, treeInfo } = searchParams;

  const reqFilter = mapFilterToReq(diffFilter);

  const isBuildTab = searchParams.currentPageTab === 'global.builds';

  const {
    isLoading: buildIsLoading,
    data: buildData,
    status: buildStatus,
    isPlaceholderData: buildIsPlaceholderData,
  } = useBuildsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
    enabled: isBuildTab,
  });

  const {
    isLoading: testsIsLoading,
    data: testsData,
    status: testStatus,
    isPlaceholderData: testIsPlaceholderData,
  } = useTestsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
    enabled: !isBuildTab || (buildStatus === 'success' && !!buildData),
  });

  const isPlaceholderData = useMemo(() => {
    return isBuildTab ? buildIsPlaceholderData : testIsPlaceholderData;
  }, [buildIsPlaceholderData, isBuildTab, testIsPlaceholderData]);

  const isLoading = useMemo(() => {
    return isBuildTab ? buildIsLoading : testsIsLoading;
  }, [isBuildTab, testsIsLoading, buildIsLoading]);

  const filterListElement = useMemo(
    () =>
      Object.keys(diffFilter).length !== 0 ? (
        <TreeDetailsFilterList
          filter={diffFilter}
          isLoading={isPlaceholderData}
        />
      ) : undefined,
    [diffFilter, isPlaceholderData],
  );

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = buildData?.summary.builds ?? {};
    const { testStatusSummary } = testsData ?? {};

    const { bootStatusSummary } = testsData ?? {};

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
      'global.builds': buildData ? (
        <BuildStatusComponent
          valid={valid}
          invalid={invalid}
          hideInconclusive
        />
      ) : (
        <></>
      ),
    };
  }, [buildData, testsData]);

  //TODO: at some point `treeUrl` should be returned in `data`
  const treeUrl = useMemo(() => {
    let url = '';
    if (!buildData) return '';
    Object.entries(buildData.builds).some(([, build]) => {
      if (build.git_repository_url) {
        url = build.git_repository_url;
        return true;
      }
    });
    return url;
  }, [buildData]);

  const treeDetailsData: ITreeDetails = useMemo(
    () => ({
      architectures: sanitizeArchs(buildData?.summary.architectures),
      configs: sanitizeConfigs(buildData?.summary.configs),
      builds: sanitizeBuilds(buildData?.builds),
      buildsSummary: sanitizeBuildsSummary(buildData?.summary.builds),
      issues: buildData?.issues || [],
    }),
    [buildData],
  );

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return (
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
          commit={treeId}
          treeNames={treeInfo?.treeName}
          tag={treeInfo?.commitName ? treeInfo?.commitName : treeId}
          gitUrl={treeInfo?.gitUrl}
        />
      </div>
      <QuerySwitcher
        status={testStatus}
        data={testsData}
        skeletonClassname="h-[200px] bg-lightGray"
      >
        <div className="mt-5">
          <MemoizedHardwareUsed
            title={<FormattedMessage id="treeDetails.hardwareUsed" />}
            hardwareUsed={testsData?.hardwareUsed}
          />
        </div>
      </QuerySwitcher>
      <div className="flex flex-col pb-2">
        <div className="sticky top-[4.5rem] z-10">
          <div className="absolute right-0 top-2 py-4">
            <TreeDetailsFilter paramFilter={diffFilter} treeUrl={treeUrl} />
          </div>
        </div>
        <TreeDetailsTab
          treeDetailsData={treeDetailsData}
          filterListElement={filterListElement}
          reqFilter={reqFilter}
          countElements={tabsCounts}
        />
      </div>
    </div>
  );
}

export default TreeDetails;
