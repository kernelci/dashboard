import type { MessageDescriptor } from 'react-intl';

import { HAS_INCIDENT_OPTION_KEY } from '@/utils/constants/issues';

type TOptionFilter = {
  displayTextId: MessageDescriptor['id'];
};

/**
 * Maps a page to the key that goes into diffFilter.
 *
 * Each key is then mapped to special property, such as displayTextId or tooltipId.
 */
export const OptionFilters: Record<string, Record<string, TOptionFilter>> = {
  issueListing: {
    [HAS_INCIDENT_OPTION_KEY]: {
      displayTextId: 'filter.issueHasIncident',
    },
  },
} as const;
