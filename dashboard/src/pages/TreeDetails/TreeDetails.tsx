import { useParams, useSearch } from '@tanstack/react-router';
import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useTreeDetails } from '@/api/TreeDetails';
import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import { AccordionItemBuilds, Results } from '@/types/tree/TreeDetails';
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

import TreeDetailsFilter, { mapFilterToReq } from './TreeDetailsFilter';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

import TreeDetailsFilterList from './TreeDetailsFilterList';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: Results;
  builds: AccordionItemBuilds[];
}

const TreeHeader = (): JSX.Element => {
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
        <TableHead>
          <FormattedMessage id="global.estimate" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="global.status" />
        </TableHead>
      </DumbTableHeader>
      <TableBody>
        <TableRow>
          {/** TODO: Replace with real data */}
          <TableCell>stable-rc</TableCell>
          <TableCell>linux-5.15.y</TableCell>
          <TableCell>5.15.150-rc1 </TableCell>
          <TableCell>
            git.kernel.org/pub/.../stable/linux-stable-rc.git
          </TableCell>
          <TableCell>2 hours</TableCell>
          <TableCell>Running</TableCell>
        </TableRow>
      </TableBody>
    </DumbBaseTable>
  );
};

function TreeDetails(): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { diffFilter } = useSearch({ from: '/tree/$treeId/' });

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
          buildErrors: value.valid ? 0 : 1,
          status: value.valid ? 'valid' : 'invalid',
          testStatus: {
            failTests: value.status?.fail_tests,
            passTests: value.status?.pass_tests,
            errorTests: value.status?.error_tests,
            skipTests: value.status?.skip_tests,
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
        <TreeHeader />
      </div>
      <div className="relative mt-10 flex flex-col pb-2">
        <div className="absolute right-0 top-0">
          <TreeDetailsFilter
            filter={diffFilter}
            treeUrl={treeUrl}
            commit={treeId}
          />
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
