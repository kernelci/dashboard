import { FormattedMessage, useIntl } from 'react-intl';

import { useMemo, type JSX } from 'react';

import { Link } from '@tanstack/react-router';

import { SearchIcon } from '@/components/Icons/SearchIcon';
import { StatusIcon } from '@/components/Icons/StatusIcons';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import type { LogData } from '@/hooks/useLogData';
import { valueOrEmpty } from '@/lib/string';

interface ILogViewerCard {
  isLoading?: boolean;
  logData?: LogData;
  variant?: 'full' | 'modal';
}

const getTreeBranchHash = (
  treeName?: string,
  branch?: string,
  commitHash?: string,
): string | undefined => {
  if (!treeName && !branch && !commitHash) {
    return undefined;
  }

  let result = [treeName, branch].filter(Boolean).join('/');
  if (commitHash) {
    result = result ? `${result} • ${commitHash}` : commitHash;
  }
  return result;
};

export const LogViewerCard = ({
  isLoading,
  logData,
  variant = 'modal',
}: ILogViewerCard): JSX.Element => {
  const { formatMessage } = useIntl();

  const logUrl = logData?.log_url;
  const itemId = logData?.id;
  const itemType = logData?.type;
  const hardware = valueOrEmpty(
    logData?.hardware,
    formatMessage({ id: 'global.unknown' }),
  );

  const fileName = useMemo(() => {
    try {
      return new URL(logUrl ?? '').pathname.split('/').pop();
    } catch {
      console.error(`Invalid URL: ${logUrl}`);
      return logUrl ?? '';
    }
  }, [logUrl]);

  const linkComponent = useMemo(() => {
    if (logUrl) {
      return (
        <>
          <Link
            to="/log-viewer"
            className="text-blue flex items-center gap-1 underline transition hover:brightness-125"
            search={s => ({
              url: logUrl,
              itemId: itemId,
              type: itemType,
              origin: s.origin,
            })}
            state={s => s}
          >
            <FormattedMessage
              id="logViewer.viewFullLog"
              values={{ fileName }}
            />
            <div className="flex w-10 justify-center">
              <SearchIcon className="text-blue w-full" />
            </div>
          </Link>
        </>
      );
    } else {
      return <FormattedMessage id="logSheet.noLogFound" />;
    }
  }, [logUrl, itemId, itemType, fileName]);

  return (
    <div className="gap-0">
      <div className="flex items-start justify-between p-4 text-lg">
        {isLoading ? (
          <FormattedMessage id="global.loading" />
        ) : (
          <>
            <div>
              <span className="font-medium">
                {getTreeBranchHash(
                  logData?.tree_name,
                  logData?.git_repository_branch,
                  logData?.git_commit_hash,
                )}
              </span>
              <div className="mb-3 text-sm">
                <FormattedMessage
                  id="title.hardwareDetails"
                  values={{
                    hardwareName: `${hardware} (${logData?.architecture})`,
                  }}
                />
              </div>
              {variant === 'modal' && linkComponent}
            </div>
            <Tooltip>
              <TooltipTrigger>
                <div className="flex max-w-max flex-row items-center gap-2 rounded-md bg-gray-200 p-3">
                  <StatusIcon status={logData?.status} /> {logData?.title}
                </div>
              </TooltipTrigger>
              <TooltipContent>{logData?.status}</TooltipContent>
            </Tooltip>
          </>
        )}
      </div>
    </div>
  );
};
