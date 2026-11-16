import type { JSX } from 'react';

import { useIntl } from 'react-intl';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';
import Section from '@/components/Section/Section';
import type { MessagesKey } from '@/locales/messages';

export const DetailsInfoCard = ({
  cardTitle,
  data,
}: {
  cardTitle: MessagesKey;
  data: ILinkWithIcon[];
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
