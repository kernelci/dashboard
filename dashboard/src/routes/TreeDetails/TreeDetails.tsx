import { useParams } from 'react-router-dom';

import { useEffect, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { MdExpandMore } from 'react-icons/md';

import TreeDetailsTab from '@/components/Tabs/TreeDetailsTab';
import ButtonWithIcon from '@/components/Button/ButtonWithIcon';
import { useTreeDetails } from '@/api/TreeDetails';

import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import { Results } from '@/types/tree/TreeDetails';

export interface ITreeDetails {
  archs: ISummaryItem[];
  configs: IListingItem[];
  builds: Results;
}

const TreeDetails = (): JSX.Element => {
  const { treeId } = useParams();
  const { data } = useTreeDetails(treeId ?? '');

  const [treeDetailsData, setTreeDetailsData] = useState<ITreeDetails>();

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

      setTreeDetailsData({
        archs: archData,
        configs: configsData,
        builds: buildSummaryData,
      });
    }
  }, [data]);

  return (
    <div className="flex flex-col pt-8">
      <div className="flex flex-col pb-2">
        <div className="flex justify-end">
          <ButtonWithIcon
            icon={<MdExpandMore />}
            label={<FormattedMessage id="global.filters" />}
          />
        </div>
        <TreeDetailsTab treeDetailsData={treeDetailsData} />
      </div>
    </div>
  );
};

export default TreeDetails;
