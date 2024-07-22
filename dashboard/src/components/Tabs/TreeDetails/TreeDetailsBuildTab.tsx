import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo, useState } from 'react';

import CardsGroup from '@/components/CardsGroup/CardsGroup';
import { Colors, IStatusChart } from '@/components/StatusChart/StatusCharts';
import { ITreeDetails } from '@/routes/TreeDetails/TreeDetails';
import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';
import Accordion from '@/components/Accordion/Accordion';
import { Button } from '@/components/ui/button';
import { IListingContent } from '@/components/ListingContent/ListingContent';
import { ISummary } from '@/components/Summary/Summary';

interface ITreeDetailsBuildTab {
  treeDetailsData?: ITreeDetails;
}

const TreeDetailsBuildTab = ({
  treeDetailsData,
}: ITreeDetailsBuildTab): JSX.Element => {
  const [filterBy, setFilterBy] = useState<'error' | 'success' | 'all'>('all');
  const accordionContent = useMemo(() => {
    return treeDetailsData?.builds.map(row => ({
      accordionData: {
        ...row,
        config: row.config ?? '-',
        compiler: row.compiler ?? '-',
        buildTime: row.buildTime ? (
          <span>
            {typeof row.buildTime === 'number'
              ? Math.floor(row.buildTime) + ' '
              : row.buildTime}
            <FormattedMessage id="global.seconds" />
          </span>
        ) : (
          '-'
        ),
        date: row.date?.split('T')[0],
        testStatus: {
          failTests: row.testStatus?.failTests,
          errorTests: row.testStatus?.errorTests,
          passTests: row.testStatus?.passTests,
          skipTests: row.testStatus?.skipTests,
        },
      },
    }));
  }, [treeDetailsData?.builds]);

  const filteredContent =
    filterBy === 'error'
      ? accordionContent?.filter(
          row =>
            row.accordionData.buildErrors && row.accordionData.buildErrors > 0,
        )
      : filterBy === 'success'
        ? accordionContent?.filter(
            row =>
              row.accordionData.status && row.accordionData.status === 'valid',
          )
        : accordionContent;

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(filteredContent?.length ?? 0, ITEMS_PER_PAGE);
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
            label: <FormattedMessage id="treeDetails.success" />,
            color: Colors.Green,
          },
          {
            value: treeDetailsData?.buildsSummary.invalid ?? 0,
            label: <FormattedMessage id="treeDetails.failed" />,
            color: Colors.Red,
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
      treeDetailsData?.buildsSummary.invalid,
      treeDetailsData?.buildsSummary.null,
      treeDetailsData?.buildsSummary.valid,
      treeDetailsData?.configs,
    ],
  );

  const onClickFilter = useCallback((type: 'error' | 'success' | 'all') => {
    setFilterBy(type);
  }, []);

  return (
    <div className="flex flex-col gap-8 pt-4">
      <CardsGroup cards={cards} />
      {filteredContent && (
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="treeDetails.builds" />
          </div>
          <div className="flex flex-row justify-between">
            <div>
              <Button
                variant="outline"
                className="rounded-l-full border border-black"
                onClick={() => onClickFilter('all')}
              >
                <FormattedMessage id="global.all" />
              </Button>
              <Button
                variant="outline"
                className="rounded-none border border-black"
                onClick={() => onClickFilter('success')}
              >
                <FormattedMessage id="global.successful" />
              </Button>
              <Button
                variant="outline"
                className="rounded-r-full border border-black"
                onClick={() => onClickFilter('error')}
              >
                <FormattedMessage id="global.errors" />
              </Button>
            </div>
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={filteredContent?.length ?? 0}
              itemsPerPage={ITEMS_PER_PAGE}
              onClickBack={onClickGoBack}
              onClickForward={onClickGoForward}
            />
          </div>
          <Accordion
            type="build"
            items={filteredContent.slice(startIndex, endIndex)}
          />
          <div className="flex justify-end">
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={filteredContent?.length ?? 0}
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
