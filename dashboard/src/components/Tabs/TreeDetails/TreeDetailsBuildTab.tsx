import { FormattedMessage } from 'react-intl';

import { useMemo } from 'react';

import CardsGroup from '@/components/CardsGroup/CardsGroup';
import { Colors } from '@/components/StatusChart/StatusCharts';
import { ITreeDetails } from '@/routes/TreeDetails/TreeDetails';
import BuildsTable from '@/components/Table/BuildsTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';

interface ITreeDetailsBuildTab {
  treeDetailsData?: ITreeDetails;
}

const TreeDetailsBuildTab = ({
  treeDetailsData,
}: ITreeDetailsBuildTab): JSX.Element => {
  const accordionContent = useMemo(() => {
    return treeDetailsData?.builds.map(row => ({
      trigger: {
        ...row,
        buildTime: `${row.buildTime?.split('.')[0]} ${(<FormattedMessage id="global.seconds" />)}`,
        date: row.date?.split(' ')[0],
      },
      content: <></>,
    }));
  }, [treeDetailsData?.builds]);

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(accordionContent?.length ?? 0, ITEMS_PER_PAGE);
  const cards = useMemo(
    () => [
      {
        title: <FormattedMessage id="treeDetails.buildStatus" />,
        type: 'chart',
        pieCentralLabel: `${
          (treeDetailsData?.buildsSummary.invalid ?? 0) +
          (treeDetailsData?.buildsSummary.valid ?? 0) +
          (treeDetailsData?.buildsSummary.null ?? 0)
        }`,
        pieCentralDescription: <FormattedMessage id="treeDetails.executed" />,
        elements: [
          {
            value: treeDetailsData?.buildsSummary.valid ?? 0,
            label: 'Valid',
            color: Colors.Green,
          },
          {
            value: treeDetailsData?.buildsSummary.invalid ?? 0,
            label: 'Invalid',
            color: Colors.Red,
          },
          {
            value: treeDetailsData?.buildsSummary.null ?? 0,
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
          <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
          <FormattedMessage
            key="treeDetails.compiler"
            id="treeDetails.compiler"
          />,
        ],
        type: 'summary',
      },
    ],
    [
      treeDetailsData?.archs,
      treeDetailsData?.buildsSummary.invalid,
      treeDetailsData?.buildsSummary.null,
      treeDetailsData?.buildsSummary.valid,
      treeDetailsData?.configs,
    ],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <CardsGroup cards={cards} />
      {accordionContent && (
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="treeDetails.builds" />
          </div>
          <div className="flex justify-end">
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={accordionContent?.length ?? 0}
              itemsPerPage={ITEMS_PER_PAGE}
              onClickBack={onClickGoBack}
              onClickForward={onClickGoForward}
            />
          </div>
          <BuildsTable
            buildsData={accordionContent?.slice(startIndex, endIndex)}
          />
          <div className="flex justify-end">
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={accordionContent?.length ?? 0}
              itemsPerPage={ITEMS_PER_PAGE}
              onClickBack={onClickGoBack}
              onClickForward={onClickGoForward}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const ITEMS_PER_PAGE = 10;

export default TreeDetailsBuildTab;
