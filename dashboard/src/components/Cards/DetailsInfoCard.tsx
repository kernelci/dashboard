import type { JSX } from 'react';

import { useIntl } from 'react-intl';

import Section, { type SubsectionLink } from '@/components/Section/Section';
import type { MessagesKey } from '@/locales/messages';

export const DetailsInfoCard = ({
  cardTitle,
  leftIcon,
  data,
}: {
  cardTitle: MessagesKey;
  leftIcon?: JSX.Element;
  data: SubsectionLink[];
}): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <Section
      card
      title={formatMessage({ id: cardTitle })}
      leftIcon={leftIcon}
      subsections={[{ infos: data }]}
    />
  );
};
