import { useParams, useSearch } from '@tanstack/react-router';
import { useMemo } from 'react';

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

import TreeDetailsFilter, { mapFilterToReq } from './TreeDetailsFilter';
import TreeDetailsTab from './Tabs/TreeDetailsTab';

import TreeDetailsFilterList from './TreeDetailsFilterList';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: Results;
  builds: AccordionItemBuilds[];
}

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
            <BreadcrumbLink to="/tree">Trees</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Tree Details</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <div className="flex flex-col pb-2">
        <div className="flex justify-end">
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
