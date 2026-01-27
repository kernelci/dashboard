import type { JSX } from 'react';
import { memo, useMemo } from 'react';

import { useIntl } from 'react-intl';

import type { ListingPaths } from '@/types/general';
import type { MessagesKey } from '@/locales/messages';

import { OpenGraphTags } from './OpenGraphTags';

const ListingOGTags = ({
  monitor,
  search,
}: {
  monitor: ListingPaths;
  search: string;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const listingDescription = useMemo(() => {
    let descriptionId: MessagesKey;

    switch (monitor) {
      case '/tree':
        descriptionId = 'treeListing.description';
        break;
      case '/hardware':
        descriptionId = 'hardwareListing.description';
        break;
      case '/issues':
        descriptionId = 'issueListing.description';
        break;
    }
    return (
      formatMessage({ id: descriptionId }) +
      (search !== ''
        ? ';\n' + formatMessage({ id: 'global.search' }) + ': ' + search
        : '')
    );
  }, [formatMessage, monitor, search]);

  const listingTitle = useMemo(() => {
    switch (monitor) {
      case '/tree':
        return formatMessage({ id: 'treeListing.title' });
      case '/hardware':
        return formatMessage({ id: 'hardwareListing.title' });
      case '/issues':
        return formatMessage({ id: 'issueListing.title' });
    }
  }, [formatMessage, monitor]);

  return (
    <OpenGraphTags title={listingTitle} description={listingDescription} />
  );
};

export const MemoizedListingOGTags = memo(ListingOGTags);
