import type { JSX, ReactNode, Ref } from 'react';

import BaseTable from '@/components/Table/BaseTable';
import { cn } from '@/lib/utils';

type TableFrameProps = {
  containerRef: Ref<HTMLDivElement>;
  tableWidth: number;
  headerComponents: JSX.Element[];
  children: ReactNode;
  className?: string;
};

/**
 * Measures available width via containerRef and sizes the bordered table frame
 * to the distributed column total (box-content so borders do not cause scroll).
 */
export const TableFrame = ({
  containerRef,
  tableWidth,
  headerComponents,
  children,
  className,
}: TableFrameProps): JSX.Element => {
  return (
    <div ref={containerRef} className="w-full overflow-x-auto">
      <BaseTable
        headerComponents={headerComponents}
        className={cn('table-fixed', className)}
        containerClassName="mx-auto box-content w-auto overflow-visible"
        containerStyle={tableWidth > 0 ? { width: tableWidth } : undefined}
        style={tableWidth > 0 ? { width: tableWidth } : undefined}
      >
        {children}
      </BaseTable>
    </div>
  );
};
