import { FormattedMessage } from 'react-intl';

import { useMemo } from 'react';

import CardsGroup from '@/components/CardsGroup/CardsGroup';
import { Colors, IStatusChart } from '@/components/StatusChart/StatusCharts';
import { ITreeDetails } from '@/routes/TreeDetails/TreeDetails';
import { ISummary } from '@/components/Summary/Summary';
import { IListingContent } from '@/components/ListingContent/ListingContent';

interface ITreeDetailsBuildTab {
  treeDetailsData?: ITreeDetails;
}

const TreeDetailsBuildTab = ({
  treeDetailsData,
}: ITreeDetailsBuildTab): JSX.Element => {
  const cards = useMemo(
    () => [
      {
        title: <FormattedMessage id="treeDetails.buildStatus" />,
        type: 'chart',
        pieCentralLabel: `${
          (treeDetailsData?.builds.invalid ?? 0) +
          (treeDetailsData?.builds.valid ?? 0) +
          (treeDetailsData?.builds.null ?? 0)
        }`,
        pieCentralDescription: <FormattedMessage id="treeDetails.executed" />,
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
      } as IStatusChart,
      {
        items: treeDetailsData?.configs ?? [],
        title: <FormattedMessage id="treeDetails.configs" />,
        type: 'listing',
      } as IListingContent,
      {
        summaryBody: treeDetailsData?.archs ?? [],
        title: <FormattedMessage id="treeDetails.summary" />,
        summaryHeaders: [
          <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
          <FormattedMessage
            key="treeDetails.compiler"
            id="treeDetails.compiler"
          />,
        ],
        type: 'summary',
      } as ISummary,
    ],
    [
      treeDetailsData?.archs,
      treeDetailsData?.builds.invalid,
      treeDetailsData?.builds.null,
      treeDetailsData?.builds.valid,
      treeDetailsData?.configs,
    ],
  );
  return (
    <div className="pt-4">
      <CardsGroup cards={cards} />
    </div>
  );
};

export default TreeDetailsBuildTab;
