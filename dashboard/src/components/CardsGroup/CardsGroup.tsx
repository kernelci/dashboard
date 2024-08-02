import { useMemo } from 'react';

import Summary, { ISummary } from '../Summary/Summary';
import BaseCard from '../Cards/BaseCard';
import ListingContent, {
  IListingContent,
} from '../ListingContent/ListingContent';
import StatusChartMemoized, { IStatusChart } from '../StatusChart/StatusCharts';

interface ICardsGroup {
  cards: (IListingContent | ISummary | IStatusChart)[];
}

interface ICardContent {
  card: IListingContent | ISummary | IStatusChart;
}

const CardsGroup = ({ cards }: ICardsGroup): JSX.Element => {
  const cardsList = useMemo(() => {
    return cards.map(card => (
      <BaseCard
        key={card.title?.key}
        title={<span>{card.title}</span> ?? ''}
        content={<CardContent card={card} />}
      />
    ));
  }, [cards]);
  return <div className="columns-2">{cardsList}</div>;
};

const CardContent = ({ card }: ICardContent): JSX.Element => {
  if (card.type === 'listing' && card.items) {
    return <ListingContent key={card.title.key} items={card.items} />;
  } else if (card.type === 'summary' && card.summaryBody) {
    return (
      <Summary
        key={card.title.key}
        summaryHeaders={card?.summaryHeaders}
        summaryBody={card?.summaryBody}
      />
    );
  } else if (card.type === 'chart') {
    const chartData = { ...card, title: undefined };
    return <StatusChartMemoized {...chartData} />;
  } else {
    return <></>;
  }
};

export default CardsGroup;
