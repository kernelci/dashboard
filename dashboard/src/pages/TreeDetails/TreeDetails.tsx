import { useNavigate, useParams, useSearch } from '@tanstack/react-router';
import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { IListingItem } from '@/components/ListingItem/ListingItem';
import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';
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

import {
  sanitizeArchs,
  sanitizeBuilds,
  sanitizeBuildsSummary,
  sanitizeConfigs,
} from '@/utils/utils';

import type { BuildStatus, TFilter, TIssue } from '@/types/general';

import MemoizedHardwareUsed from '@/components/Cards/HardwareUsed';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import type { ISummaryItem } from '@/components/Tabs/Summary';

import { useTreeDetails } from '@/api/treeDetails';

import { truncateUrl } from '@/lib/string';

import CopyButton from '@/components/Button/CopyButton';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';

import TreeDetailsFilter from './TreeDetailsFilter';
import type { TreeDetailsTabRightElement } from './Tabs/TreeDetailsTab';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

export interface ITreeDetails {
  architectures: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: BuildStatus;
  builds: AccordionItemBuilds[];
  buildsIssues: TIssue[];
  failedBuildsWithUnknownIssues?: number;
}

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

  const { isLoading, data, status, isPlaceholderData, error } = useTreeDetails({
    treeId: treeId ?? '',
    filter: reqFilter,
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
    });
  }, [navigate]);

  const filterListElement = useMemo(
    () => (
      <DetailsFilterList
        filter={diffFilter}
        cleanFilters={cleanAll}
        navigate={onFilterChange}
        isLoading={isPlaceholderData}
      />
    ),
    [cleanAll, diffFilter, isPlaceholderData, onFilterChange],
  );

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = data?.buildsSummary.builds ?? {};
    const { testStatusSummary } = data ?? {};

    const { bootStatusSummary } = data ?? {};

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

  const treeDetailsData: ITreeDetails = useMemo(
    () => ({
      architectures: sanitizeArchs(data?.buildsSummary.architectures),
      configs: sanitizeConfigs(data?.buildsSummary.configs),
      builds: sanitizeBuilds(data?.builds),
      buildsSummary: sanitizeBuildsSummary(data?.buildsSummary.builds),
      buildsIssues: data?.buildsIssues || [],
      failedBuildsWithUnknownIssues: data?.failedBuildsWithUnknownIssues,
    }),
    [data],
  );

  return (
    <QuerySwitcher
      status={status}
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
            commitTags={data?.git_commit_tags}
          />
        </div>
        <QuerySwitcher
          status={status}
          data={data}
          skeletonClassname="h-[200px] bg-lightGray"
        >
          <div className="mt-5">
            <MemoizedHardwareUsed
              title={<FormattedMessage id="treeDetails.hardwareUsed" />}
              hardwareUsed={data?.hardwareUsed}
              diffFilter={diffFilter}
            />
          </div>
        </QuerySwitcher>
        <div className="flex flex-col pb-2">
          {data?.treeUrl && (
            <div className="sticky top-[4.5rem] z-10">
              <div className="absolute right-0 top-2 py-4">
                <TreeDetailsFilter
                  paramFilter={diffFilter}
                  treeUrl={data.treeUrl}
                />
              </div>
            </div>
          )}
          <TreeDetailsTab
            treeDetailsData={treeDetailsData}
            filterListElement={filterListElement}
            reqFilter={reqFilter}
            countElements={tabsCounts}
          />
        </div>
      </div>
    </QuerySwitcher>
  );
}

export default TreeDetails;
