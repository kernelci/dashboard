import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type {
  CompareItemStatus,
  CompareRowChange,
} from '@/types/tree/TreeCompare';

import type { MessagesKey } from '@/locales/messages';

import { cn } from '@/lib/utils';

const STATUS_STYLES: Record<CompareItemStatus, string> = {
  PASS: 'bg-light-green text-dark-green',
  FAIL: 'bg-light-red text-red',
  INCONCLUSIVE: 'bg-medium-gray text-dim-gray',
  '—': 'bg-medium-gray text-dim-gray',
};

export function CompareStatusChip({
  status,
}: {
  status: CompareItemStatus;
}): JSX.Element {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center rounded-full px-2.5 py-1 text-xs font-semibold',
        STATUS_STYLES[status],
      )}
    >
      {status}
    </span>
  );
}

const CHANGE_STYLES: Record<CompareRowChange, string> = {
  regression: 'bg-light-red text-red',
  fixed: 'bg-light-green text-dark-green',
  newFailure: 'bg-orange-100 text-orange-700',
  stillFailing: 'bg-medium-gray text-dim-gray',
  newPass: 'bg-light-blue text-dark-blue',
  appeared: 'bg-yellow text-dim-black',
  disappeared: 'bg-dark-gray text-dim-gray',
  unchanged: 'bg-medium-gray text-dim-gray',
};

const CHANGE_MESSAGE_IDS: Record<CompareRowChange, MessagesKey> = {
  regression: 'treeCompare.change.regression',
  fixed: 'treeCompare.change.fixed',
  newFailure: 'treeCompare.change.newFailure',
  stillFailing: 'treeCompare.change.stillFailing',
  newPass: 'treeCompare.change.newPass',
  appeared: 'treeCompare.change.appeared',
  disappeared: 'treeCompare.change.disappeared',
  unchanged: 'treeCompare.change.unchanged',
};

export function CompareChangeBadge({
  change,
}: {
  change: CompareRowChange;
}): JSX.Element {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        CHANGE_STYLES[change],
      )}
    >
      <FormattedMessage id={CHANGE_MESSAGE_IDS[change]} />
    </span>
  );
}

export function isFailureHighlight(change: CompareRowChange): boolean {
  return (
    change === 'regression' ||
    change === 'newFailure' ||
    change === 'stillFailing'
  );
}
