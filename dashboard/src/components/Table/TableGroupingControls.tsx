import type { JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { PillButton } from '@/components/Button/FilterButton';
import type { MessagesKey } from '@/locales/messages';

export type TableGroupingMode = 'grouped' | 'ungrouped';

export interface ITableGroupingControls {
  mode: TableGroupingMode;
  onModeChange: (mode: TableGroupingMode) => void;
  onExpandAll: () => void;
  onCollapseAll: () => void;
}

type GroupingButton = {
  key: string;
  labelId: MessagesKey;
  onClick: () => void;
};

/**
 * Expand / collapse / disable-grouping controls for tables that use
 * TanStack row expansion / hierarchical grouping.
 */
export function TableGroupingControls({
  mode,
  onModeChange,
  onExpandAll,
  onCollapseAll,
}: ITableGroupingControls): JSX.Element {
  const buttons: GroupingButton[] =
    mode === 'grouped'
      ? [
          {
            key: 'expand',
            labelId: 'table.grouping.expandAll',
            onClick: onExpandAll,
          },
          {
            key: 'collapse',
            labelId: 'table.grouping.collapseAll',
            onClick: onCollapseAll,
          },
          {
            key: 'disable',
            labelId: 'table.grouping.disable',
            onClick: (): void => onModeChange('ungrouped'),
          },
        ]
      : [
          {
            key: 'enable',
            labelId: 'table.grouping.enable',
            onClick: (): void => onModeChange('grouped'),
          },
        ];

  return (
    <div className="flex flex-col gap-2 sm:items-end">
      <span className="text-dim-gray text-sm">
        <FormattedMessage id="table.grouping.label" />
      </span>
      <div className="flex flex-wrap gap-2 sm:justify-end">
        {buttons.map(button => (
          <PillButton key={button.key} onClick={button.onClick}>
            <FormattedMessage id={button.labelId} />
          </PillButton>
        ))}
      </div>
    </div>
  );
}
