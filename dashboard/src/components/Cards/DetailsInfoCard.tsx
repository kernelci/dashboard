import type { JSX, ReactNode } from 'react';

import { useIntl } from 'react-intl';

import Section, { type SubsectionLink } from '@/components/Section/Section';
import type { MessagesKey } from '@/locales/messages';

export const DetailsInfoCard = ({
  cardTitle,
  title,
  data,
}: {
  cardTitle?: MessagesKey;
  title?: ReactNode;
  data: SubsectionLink[];
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const sectionTitle =
    title ?? (cardTitle ? formatMessage({ id: cardTitle }) : '');

  return (
    <Section card title={sectionTitle} subsections={[{ infos: data }]} />
  );
};