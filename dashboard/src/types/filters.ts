import type { MessageDescriptor } from 'react-intl';

import { HAS_INCIDENT_OPTION } from '@/utils/constants/issues';

type TOptionFilter = {
  displayTextId: MessageDescriptor['id'];
};

/**
 * Maps a page to option filter values that go into diffFilter, adding more properties to those values.
 *
 * Those properties can then be used in the checkbox section, such as displayTextId.
 *
 * Example:
 * ```
 * {
 *   issueListing: {
 *     "hasIncident": {
 *       displayTextId: 'filter.issueHasIncident'
 *     }
 *   }
 * }
 * ```
 */
export const OptionFilters: Record<string, Record<string, TOptionFilter>> = {
  issueListing: {
    [HAS_INCIDENT_OPTION]: {
      displayTextId: 'filter.issueHasIncident',
    },
  },
} as const;
