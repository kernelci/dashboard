import { useMemo } from 'react';

import Summary, { ISummary } from '../Summary/Summary';
import BaseCard from '../Cards/BaseCard';
import ListingContent, {
  IListingContent,
} from '../ListingContent/ListingContent';

interface ICardsGroup {
  cards: (IListingContent | ISummary)[];
}

interface ICardContent {
  card: IListingContent | ISummary;
}

const CardsGroup = ({ cards }: ICardsGroup): JSX.Element => {
  const cardsList = useMemo(() => {
    return cards.map(card => (
      <BaseCard
        key={card.title.key}
        title={card.title}
        content={<CardContent card={card} />}
      />
    ));
  }, [cards]);
  return <div className="grid grid-cols-2 gap-8">{cardsList}</div>;
};

const CardContent = ({ card }: ICardContent): JSX.Element => {
  if (card.type === 'listing' && card.items) {
    return <ListingContent key={card.title.key} items={card.items} />;
  } else if (card.type === 'summary' && card.summaryBody) {
    return (
      <Summary
        key=""
        summaryHeaders={card?.summaryHeaders}
        summaryBody={card?.summaryBody}
      />
    );
  } else {
    return <></>;
  }
};

export default CardsGroup;
