import { useParams } from 'react-router-dom';

import { useEffect, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { MdExpandMore } from 'react-icons/md';

import TreeDetailsTab from '@/components/Tabs/TreeDetailsTab';
import ButtonWithIcon from '@/components/Button/ButtonWithIcon';
import { useTreeDetails } from '@/api/TreeDetails';

import { IListingItem } from '@/components/ListingItem/ListingItem';
import { ISummaryItem } from '@/components/Summary/Summary';
import CardsGroup from '@/components/CardsGroup/CardsGroup';
import { Colors } from '@/components/StatusChart/StatusCharts';
import { Results } from '@/types/tree/TreeDetails';

interface ITreeDetails {
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
      <div className="flex flex-row pb-2 border-b border-darkGray">
        <TreeDetailsTab />
        <ButtonWithIcon
          icon={<MdExpandMore />}
          label={<FormattedMessage id="global.filters" />}
        />
      </div>
      <div className="pt-4">
        <CardsGroup
          cards={[
            {
              title: <FormattedMessage id="treeDetails.buildStatus" />,
              type: 'chart',
              pieCentralLabel: `${
                (treeDetailsData?.builds.invalid ?? 0) +
                (treeDetailsData?.builds.valid ?? 0) +
                (treeDetailsData?.builds.null ?? 0)
              }`,
              pieCentralDescription: (
                <FormattedMessage id="treeDetails.executed" />
              ),
              elements: [
                {
                  value: treeDetailsData?.builds.valid ?? 0,
                  label: 'Valid',
                  color: Colors.Green,
                },
                {
                  value: treeDetailsData?.builds.invalid ?? 0,
                  label: 'Invalid',
                  color: Colors.Red,
                },
                {
                  value: treeDetailsData?.builds.null ?? 0,
                  label: 'Null',
                  color: Colors.Gray,
                },
              ],
            },
            {
              items: treeDetailsData?.configs ?? [],
              title: <FormattedMessage id="treeDetails.configs" />,
              type: 'listing',
            },
            {
              summaryBody: treeDetailsData?.archs ?? [],
              title: <FormattedMessage id="treeDetails.summary" />,
              summaryHeaders: [
                <FormattedMessage
                  key="treeDetails.arch"
                  id="treeDetails.arch"
                />,
                <FormattedMessage
                  key="treeDetails.compiler"
                  id="treeDetails.compiler"
                />,
              ],
              type: 'summary',
            },
          ]}
        />
      </div>
    </div>
  );
};

export default TreeDetails;
