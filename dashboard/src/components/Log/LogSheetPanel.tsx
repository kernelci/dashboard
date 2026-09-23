import { type JSX } from 'react';

import { LogExcerpt } from '@/components/Log/LogExcerpt';
import { LogViewerCard } from '@/components/Log/LogViewerCard';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { useLogExcerpt } from '@/api/logViewer';
import type { LogData } from '@/hooks/useLogData';

interface LogSheetPanelProps {
  logData?: LogData;
  isLoading?: boolean;
  variant?: 'full' | 'modal' | 'compare';
}

export const LogSheetPanel = ({
  logData,
  isLoading,
  variant = 'modal',
}: LogSheetPanelProps): JSX.Element => {
  const excerptQuery = useLogExcerpt(logData?.log_excerpt);

  return (
    <>
      <LogViewerCard
        logData={logData}
        isLoading={isLoading}
        variant={variant}
      />
      <QuerySwitcher data={excerptQuery.data} status={excerptQuery.status}>
        <LogExcerpt
          logExcerpt={excerptQuery.data?.content}
          isLoading={isLoading}
          variant="default"
        />
      </QuerySwitcher>
    </>
  );
};
