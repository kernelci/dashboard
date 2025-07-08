import { FormattedMessage, useIntl } from 'react-intl';

import { useMemo, type JSX } from 'react';

import { Link, useRouterState } from '@tanstack/react-router';

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
  const architecture = valueOrEmpty(
    logData?.architecture,
    formatMessage({ id: 'global.unknownArchitecture' }),
  );

  const fileName = useMemo(() => {
    try {
      return new URL(logUrl ?? '').pathname.split('/').pop();
    } catch {
      console.error(`Invalid URL: ${logUrl}`);
      return logUrl ?? '';
    }
  }, [logUrl]);

  const { treeName, branch, id } = useRouterState({
    select: s => s.location.state,
  });

  const logDataTreeName = logData?.tree_name;
  const logDataBranch = logData?.git_repository_branch;
  const logDataHash = logData?.git_commit_hash;

  const stateIsSetted = treeName && branch && id;
  const stateParams = useMemo(
    () =>
      !stateIsSetted
        ? { treeName: logDataTreeName, branch: logDataBranch, id: logDataHash }
        : {},
    [stateIsSetted, logDataTreeName, logDataBranch, logDataHash],
  );

  const linkComponent = useMemo(() => {
    if (logUrl) {
      return (
        <div className="mt-3">
          <Link
            to="/log-viewer"
            className="text-blue flex items-center gap-1 underline transition hover:brightness-125"
            search={s => ({
              url: logUrl,
              itemId: itemId,
              type: itemType,
              origin: s.origin,
            })}
            state={s => ({ ...s, ...stateParams })}
          >
            <FormattedMessage
              id="logViewer.viewFullLog"
              values={{ fileName }}
            />
            <div className="flex w-10 justify-center">
              <SearchIcon className="text-blue w-full" />
            </div>
          </Link>
        </div>
      );
    } else {
      return (
        <div className="mt-3">
          <FormattedMessage id="logSheet.noLogFound" />
        </div>
      );
    }
  }, [logUrl, itemId, itemType, fileName, stateParams]);

  const hardwareLabel = useMemo(() => {
    return `${hardware} (${architecture})`;
  }, [hardware, architecture]);

  return (
    <div className="gap-0">
      <div className="flex items-start justify-between p-4 text-lg">
        {isLoading ? (
          <FormattedMessage id="global.loading" />
        ) : (
          <>
            <div>
              <div className="font-medium">
                {getTreeBranchHash(
                  logData?.tree_name,
                  logData?.git_repository_branch,
                  logData?.git_commit_hash,
                )}
              </div>
              {logData?.type !== 'build' && (
                <div className="mb-3 text-sm">
                  <FormattedMessage
                    id="title.hardwareDetails"
                    values={{
                      hardwareName: hardwareLabel,
                    }}
                  />
                </div>
              )}
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
