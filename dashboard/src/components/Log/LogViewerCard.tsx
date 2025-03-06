import { FormattedMessage } from 'react-intl';
import { LuFileJson } from 'react-icons/lu';

import { useMemo, type JSX } from 'react';

import { Link } from '@tanstack/react-router';

import BaseCard from '@/components/Cards/BaseCard';

interface ILogViewerCard {
  isLoading?: boolean;
  logUrl?: string;
}

export const LogViewerCard = ({
  isLoading,
  logUrl,
}: ILogViewerCard): JSX.Element => {
  const fileName = useMemo(() => {
    try {
      return new URL(logUrl ?? '').pathname.split('/').pop();
    } catch {
      console.error(`Invalid URL: ${logUrl}`);
      return logUrl ?? '';
    }
  }, [logUrl]);
  return (
    <BaseCard
      className="gap-0"
      title={<FormattedMessage id="global.fullLogs" />}
    >
      <div className="p-4 text-lg font-medium">
        {isLoading ? (
          <FormattedMessage id="global.loading" />
        ) : (
          <>
            {logUrl ? (
              <>
                <Link
                  to="/log-viewer"
                  className="flex items-center gap-1 underline transition hover:brightness-125"
                  search={s => ({ url: logUrl ?? '', origin: s.origin })}
                  title="Log Viewer"
                >
                  <FormattedMessage
                    id="logViewer.viewFullLog"
                    values={{ fileName }}
                  />
                  <div className="flex w-10 justify-center">
                    <LuFileJson className="text-blue w-full" />
                  </div>
                </Link>
              </>
            ) : (
              <FormattedMessage id="logSheet.noLogFound" />
            )}
          </>
        )}
      </div>
    </BaseCard>
  );
};
