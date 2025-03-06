import { useSearch } from '@tanstack/react-router';
import type { JSX } from 'react';

const Constants = {
  URL_DOMAIN_SIZE: 90,
  URL_END_PATH_SIZE: 50,
} as const;

import { FormattedMessage } from 'react-intl';

import { LogExcerpt } from '@/components/Log/LogExcerpt';
import { truncateUrl } from '@/lib/string';
import { useLogViewer } from '@/api/logViewer';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

export function LogViewer(): JSX.Element {
  const { url } = useSearch({ from: '/log-viewer' });

  const { data, status } = useLogViewer(url);

  return (
    <main className="bg-light-gray min-h-[100vh] border-2 px-8 pt-14 pb-3">
      <div className="mb-3 px-3">
        <h1 className="mb-3 text-4xl font-medium">Log Viewer</h1>
        <div className="px-0">
          <p className="text-xl">
            <FormattedMessage id="logViewer.download" />
          </p>
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="hover:text-blue text-dark-blue underline transition"
          >
            {truncateUrl(
              url,
              Constants.URL_DOMAIN_SIZE,
              Constants.URL_END_PATH_SIZE,
            )}
          </a>
        </div>
      </div>
      <div className="overflow-hidden rounded-md">
        <QuerySwitcher data={data} status={status}>
          <LogExcerpt logExcerpt={data?.content} variant="log-viewer" />
        </QuerySwitcher>
      </div>
    </main>
  );
}
