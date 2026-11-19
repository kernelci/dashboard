import type { JSX } from 'react';

import { useIntl } from 'react-intl';

import Section, { type SubsectionLink } from '@/components/Section/Section';
import type { MessagesKey } from '@/locales/messages';

export const DetailsInfoCard = ({
  cardTitle,
  data,
}: {
  cardTitle: MessagesKey;
  data: SubsectionLink[];
}): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <Section
      card
      title={formatMessage({ id: cardTitle })}
      subsections={[{ infos: data }]}
    />
  );
};
