import classNames from 'classnames';
import type { JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { Button } from '@/components/ui/button';
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
    <div className="flex flex-col items-end">
      <span className="mr-4">
        <FormattedMessage id="table.grouping.label" />
      </span>
      <span className="flex flex-wrap justify-end">
        {buttons.map((button, index) => (
          <Button
            variant="outline"
            key={button.key}
            className={classNames(
              'hover:bg-light-blue border border-black bg-transparent text-black',
              index === 0 ? 'rounded-l-full' : 'rounded-l-none',
              index === buttons.length - 1
                ? 'rounded-r-full'
                : 'rounded-r-none',
            )}
            onClick={button.onClick}
          >
            <FormattedMessage id={button.labelId} />
          </Button>
        ))}
      </span>
    </div>
  );
}
