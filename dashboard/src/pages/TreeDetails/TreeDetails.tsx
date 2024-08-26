import { useParams, useSearch } from '@tanstack/react-router';
import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useTreeDetails } from '@/api/TreeDetails';
import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import {
  AccordionItemBuilds,
  Results,
  TreeDetailsBuild,
} from '@/types/tree/TreeDetails';
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

import TreeDetailsFilter, { mapFilterToReq } from './TreeDetailsFilter';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

import TreeDetailsFilterList from './TreeDetailsFilterList';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: Results;
  builds: AccordionItemBuilds[];
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
            {sanitizeTableValue(
              tag && tag !== '' ? tag : commit && commit !== '' ? commit : '-',
            )}
          </TableCell>
          <TableCell>{gitUrl ?? '-'}</TableCell>
        </TableRow>
      </TableBody>
    </DumbBaseTable>
  );
};

const isBuildError = (build: TreeDetailsBuild): number => {
  return build.valid || build.valid === null ? 0 : 1;
};

function TreeDetails(): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { diffFilter, treeInfo } = useSearch({
    from: '/tree/$treeId/',
  });

  const reqFilter = mapFilterToReq(diffFilter);

  const { data } = useTreeDetails(treeId ?? '', reqFilter);

  const filterListElement = useMemo(
    () => <TreeDetailsFilterList filter={diffFilter} />,
    [diffFilter],
  );

  //TODO: at some point `treeUrl` should be returned in `data`
  const treeUrl = useMemo(() => {
    let url = '';
    if (!data) return '';
    Object.entries(data.builds).some(([, build]) => {
      if (build.git_repository_url) {
        url = build.git_repository_url;
        return true;
      }
    });
    return url;
  }, [data]);

  const treeDetailsData: ITreeDetails | undefined = useMemo(() => {
    if (data) {
      const configsData: IListingItem[] = Object.entries(
        data.summary.configs,
      ).map(([key, value]) => ({
        text: key,
        errors: value.invalid,
        success: value.valid,
      }));

      const archData: ISummaryItem[] = Object.entries(
        data.summary.architectures,
      ).map(([key, value]) => ({
        arch: { text: key, errors: value.invalid, success: value.valid },
        compilers: value.compilers,
      }));

      const buildSummaryData: Results = {
        valid: data.summary.builds.valid,
        invalid: data.summary.builds.invalid,
        null: data.summary.builds.null,
      };

      const buildsData: AccordionItemBuilds[] = Object.entries(data.builds).map(
        ([, value]) => ({
          id: value.id,
          config: value.config_name,
          date: value.start_time,
          buildTime: value.duration,
          compiler: value.compiler,
          buildErrors: isBuildError(value),
          status:
            value.valid === null ? 'null' : value.valid ? 'valid' : 'invalid',
          testStatus: {
            failTests: value.status?.fail_tests,
            passTests: value.status?.pass_tests,
            errorTests: value.status?.error_tests,
            skipTests: value.status?.skip_tests,
            missTests: value.status?.miss_tests,
            doneTests: value.status?.done_tests,
          },
          buildLogs: value.log_url,
          kernelConfig: value.config_url,
          kernelImage: value.misc ? value.misc['kernel_type'] : undefined,
          dtb: value.misc ? value.misc['dtb'] : undefined,
          systemMap: value.misc ? value.misc['system_map'] : undefined,
          modules: value.misc ? value.misc['modules'] : undefined,
        }),
      );

      return {
        archs: archData,
        configs: configsData,
        buildsSummary: buildSummaryData,
        builds: buildsData,
      };
    }
  }, [data]);

  return (
    <div className="flex flex-col pt-8">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink to="/tree">
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
      <div className="relative mt-10 flex flex-col pb-2">
        <div className="absolute right-0 top-0">
          <TreeDetailsFilter paramFilter={diffFilter} treeUrl={treeUrl} />
        </div>
        <TreeDetailsTab
          treeDetailsData={treeDetailsData}
          filterListElement={filterListElement}
        />
      </div>
    </div>
  );
}

export default TreeDetails;
