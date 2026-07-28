import { RotateCcw } from 'lucide-react';
import type { JSX } from 'react';
import { useIntl } from 'react-intl';

import { Button } from '@/components/ui/button';

type ColumnResetWidthButtonProps = {
  onReset: () => void;
};

export const ColumnResetWidthButton = ({
  onReset,
}: ColumnResetWidthButtonProps): JSX.Element => {
  const intl = useIntl();

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="h-6 w-6 shrink-0"
      onClick={event => {
        event.stopPropagation();
        onReset();
      }}
      aria-label={intl.formatMessage({ id: 'table.resetColumnWidth' })}
      title={intl.formatMessage({ id: 'table.resetColumnWidth' })}
    >
      <RotateCcw className="h-3 w-3" />
    </Button>
  );
};
