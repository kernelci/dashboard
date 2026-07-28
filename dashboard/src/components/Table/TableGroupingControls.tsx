import classNames from 'classnames';
import { useMemo, type JSX } from 'react';
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
  isSelected: boolean;
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
  const isGrouped = mode === 'grouped';

  const buttons = useMemo((): GroupingButton[] => {
    if (!isGrouped) {
      return [
        {
          key: 'enable',
          labelId: 'table.grouping.enable',
          onClick: (): void => onModeChange('grouped'),
          isSelected: false,
        },
      ];
    }

    return [
      {
        key: 'expand',
        labelId: 'table.grouping.expandAll',
        onClick: onExpandAll,
        isSelected: false,
      },
      {
        key: 'collapse',
        labelId: 'table.grouping.collapseAll',
        onClick: onCollapseAll,
        isSelected: false,
      },
      {
        key: 'disable',
        labelId: 'table.grouping.disable',
        onClick: (): void => onModeChange('ungrouped'),
        isSelected: false,
      },
    ];
  }, [isGrouped, onCollapseAll, onExpandAll, onModeChange]);

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
              'hover:bg-light-blue border border-black',
              index === 0 ? 'rounded-l-full' : 'rounded-l-none',
              index === buttons.length - 1
                ? 'rounded-r-full'
                : 'rounded-r-none',
              button.isSelected
                ? 'bg-blue text-white'
                : 'bg-transparent text-black',
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
