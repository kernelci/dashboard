import { useMemo } from 'react';

import Summary, { ISummary } from '../Summary/Summary';
import BaseCard from '../Cards/BaseCard';
import ListingContent, {
  IListingContent,
} from '../ListingContent/ListingContent';
import StatusChartMemoized, { IStatusChart } from '../StatusChart/StatusCharts';

type TPossibleCard = (IListingContent | ISummary | IStatusChart) & {
  key: string;
};

interface ICardsGroup {
  cards: TPossibleCard[];
}

interface ICardContent {
  card: IListingContent | ISummary | IStatusChart;
}

const CardsGroup = ({ cards }: ICardsGroup): JSX.Element => {
  const cardsList = useMemo(() => {
    return cards.map(card => {
      return (
        <BaseCard
          key={card.key}
          title={<span>{card.title}</span> ?? ''}
          content={<CardContent card={card} />}
        />
      );
    });
  }, [cards]);
  return <div className="columns-2">{cardsList}</div>;
};

const CardContent = ({ card }: ICardContent): JSX.Element => {
  if (card.type === 'listing' && card.items) {
    return (
      <ListingContent
        key={card.title.key}
        items={card.items}
        onClickItem={card.onClickItem}
      />
    );
  } else if (card.type === 'summary' && card.summaryBody) {
    return (
      <Summary
        key={card.title.key}
        summaryHeaders={card?.summaryHeaders}
        onClickKey={card?.onClickKey}
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
