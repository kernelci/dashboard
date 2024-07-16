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

const TreeDetails = (): JSX.Element => {
  const { treeId } = useParams();
  const { data } = useTreeDetails(treeId ?? '');

  const [configs, setConfigs] = useState<IListingItem[]>();
  const [archictectures, setArchitectures] = useState<ISummaryItem[]>();

  useEffect(() => {
    if (data) {
      const configsData: IListingItem[] = Object.entries(
        data.summary.configs,
      ).map(([key, value]) => ({
        text: key,
        errors: value.invalid,
        success: value.valid,
      }));
      setConfigs(configsData);

      const archData: ISummaryItem[] = Object.entries(
        data.summary.architectures,
      ).map(([key, value]) => ({
        arch: { text: key, errors: value.invalid, success: value.valid },
        compilers: value.compilers,
      }));

      setArchitectures(archData);
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
              items: configs ?? [],
              title: <FormattedMessage id="treeDetails.configs" />,
              type: 'listing',
            },
            {
              summaryBody: archictectures ?? [],
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
