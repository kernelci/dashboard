import { useParams } from 'react-router-dom';

import { useEffect, useState, useMemo } from 'react';

import { useTreeDetails } from '@/api/TreeDetails';
import TreeDetailsTab from '@/components/Tabs/TreeDetailsTab';
import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import { AccordionItemBuilds, Results } from '@/types/tree/TreeDetails';

import TreeDetailsFilter, {
  createFilter,
  mapFilterToReq,
  TFilter,
} from './TreeDetailsFilter';

import TreeDetailsFilterList from './TreeDetailsFilterList';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: Results;
  builds: AccordionItemBuilds[];
}

const TreeDetails = (): JSX.Element => {
  const { treeId } = useParams();
  const [filter, setFilter] = useState<TFilter>({});
  const reqFilter = mapFilterToReq(filter);

  const { data } = useTreeDetails(treeId ?? '', reqFilter);

  const [treeDetailsData, setTreeDetailsData] = useState<ITreeDetails>();

  if (data && Object.keys(filter).length === 0) {
    setFilter(createFilter(data));
  }

  const filterListElement = useMemo(
    () => <TreeDetailsFilterList filter={filter} onFilter={setFilter} />,
    [filter],
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

  useEffect(() => {
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

      setTreeDetailsData({
        archs: archData,
        configs: configsData,
        buildsSummary: buildSummaryData,
        builds: buildsData,
      });
    }
  }, [data]);

  return (
    <div className="flex flex-col pt-8">
      <div className="flex flex-col pb-2">
        <div className="flex justify-end">
          <TreeDetailsFilter
            filter={filter}
            onFilter={setFilter}
            treeUrl={treeUrl}
          />
        </div>
        <TreeDetailsTab
          treeDetailsData={treeDetailsData}
          filterListElement={filterListElement}
        />
      </div>
    </div>
  );
};

export default TreeDetails;
