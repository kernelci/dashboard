import { useParams } from 'react-router-dom';

import { useEffect, useState, useRef } from 'react';

import { useTreeDetails } from '@/api/TreeDetails';
import TreeDetailsTab from '@/components/Tabs/TreeDetailsTab';
import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import {
  AccordionItemBuilds,
  Results,
  TTreeDetailsFilter,
  TreeDetails as TreeDetailsType,
} from '@/types/tree/TreeDetails';

import TreeDetailsFilter from './TreeDetailsFilter';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  buildsSummary: Results;
  builds: AccordionItemBuilds[];
}

const TreeDetails = (): JSX.Element => {
  const { treeId } = useParams();
  const [filter, setFilter] = useState<
    TTreeDetailsFilter | Record<string, never>
  >({});
  const { data } = useTreeDetails(treeId ?? '', filter);

  const [treeDetailsData, setTreeDetailsData] = useState<ITreeDetails>();
  const initialDataRef = useRef<TreeDetailsType | undefined>();
  if (!initialDataRef.current) {
    initialDataRef.current = data;
  }

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
            data={initialDataRef.current}
            onFilter={setFilter}
          />
        </div>
        <TreeDetailsTab treeDetailsData={treeDetailsData} />
      </div>
    </div>
  );
};

export default TreeDetails;
