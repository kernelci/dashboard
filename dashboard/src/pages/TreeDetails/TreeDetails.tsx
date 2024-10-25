import { useParams, useSearch } from '@tanstack/react-router';
import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useBuildsTab, useTestsTab } from '@/api/TreeDetails';
import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import {
  AccordionItemBuilds,
  BuildStatus,
  BuildsTab,
  BuildsTabBuild,
} from '@/types/tree/TreeDetails';
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

import TreeDetailsFilter, { mapFilterToReq } from './TreeDetailsFilter';
import TreeDetailsTab, {
  TreeDetailsTabRightElement,
} from './Tabs/TreeDetailsTab';

import TreeDetailsFilterList from './TreeDetailsFilterList';
import { MemoizedHardwareUsed } from './Tabs/TestCards';

export interface ITreeDetails {
  archs: ISummaryItem[];
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
          <FormattedMessage id="global.branch" />
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

const isBuildError = (build: BuildsTabBuild): number => {
  return build.valid || build.valid === null ? 0 : 1;
};

function TreeDetails(): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const searchParams = useSearch({ from: '/tree/$treeId/' });
  const { diffFilter, treeInfo } = searchParams;

  const reqFilter = mapFilterToReq(diffFilter);

  const isBuildTab =
    searchParams.currentTreeDetailsTab === 'treeDetails.builds';

  const {
    isLoading: buildIsLoading,
    data: buildData,
    status: buildStatus,
  } = useBuildsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
    enabled: isBuildTab,
  });

  const {
    isLoading: testsIsLoading,
    data: testsData,
    status: testStatus,
  } = useTestsTab({
    treeId: treeId ?? '',
    filter: reqFilter,
    enabled: !isBuildTab || (buildStatus === 'success' && !!buildData),
  });

  const isLoading = useMemo(() => {
    return isBuildTab ? buildIsLoading : testsIsLoading;
  }, [isBuildTab, testsIsLoading, buildIsLoading]);

  const filterListElement = useMemo(
    () => <TreeDetailsFilterList filter={diffFilter} />,
    [diffFilter],
  );

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = buildData?.summary.builds ?? {};
    const { testStatusSummary } = testsData ?? {};

    const { bootStatusSummary } = testsData ?? {};

    return {
      'treeDetails.tests': testStatusSummary ? (
        <GroupedTestStatus
          fail={testStatusSummary.FAIL}
          pass={testStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'treeDetails.boots': bootStatusSummary ? (
        <GroupedTestStatus
          fail={bootStatusSummary.FAIL}
          pass={bootStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'treeDetails.builds': buildData ? (
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

  const treeDetailsData: ITreeDetails | undefined = useMemo(() => {
    if (buildData) {
      const configsData: IListingItem[] = Object.entries(
        buildData.summary.configs,
      ).map(([key, value]) => ({
        text: key,
        errors: value.invalid,
        success: value.valid,
        unknown: value.null,
      }));

      const archData: ISummaryItem[] = Object.entries(
        buildData.summary.architectures,
      ).map(([key, value]) => ({
        arch: {
          text: key,
          errors: value.invalid,
          success: value.valid,
          unknown: value.null,
        },
        compilers: value.compilers,
      }));

      const buildSummaryData: BuildStatus = {
        valid: buildData.summary.builds.valid,
        invalid: buildData.summary.builds.invalid,
        null: buildData.summary.builds.null,
      };

      const buildsData: AccordionItemBuilds[] = Object.entries(
        buildData.builds,
      ).map(([, value]) => ({
        id: value.id,
        config: value.config_name,
        date: value.start_time,
        buildTime: value.duration,
        compiler: value.compiler,
        buildErrors: isBuildError(value),
        status:
          value.valid === null ? 'null' : value.valid ? 'valid' : 'invalid',
        buildLogs: value.log_url,
        kernelConfig: value.config_url,
        kernelImage: value.misc ? value.misc['kernel_type'] : undefined,
        dtb: value.misc ? value.misc['dtb'] : undefined,
        systemMap: value.misc ? value.misc['system_map'] : undefined,
        modules: value.misc ? value.misc['modules'] : undefined,
      }));

      return {
        archs: archData,
        configs: configsData,
        buildsSummary: buildSummaryData,
        builds: buildsData,
        issues: buildData.issues,
      };
    }
  }, [buildData]);

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
            <BreadcrumbLink to="/tree" search={searchParams}>
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
      <div className="relative mt-10 flex flex-col pb-2">
        <div className="absolute right-0 top-[-16px]">
          <TreeDetailsFilter paramFilter={diffFilter} treeUrl={treeUrl} />
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
